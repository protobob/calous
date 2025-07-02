use std::env;
use std::io::{self, Read, Write};
use std::os::unix::net::UnixStream;
use std::fs;
use std::path::PathBuf;

use serde::{Deserialize, Serialize};
use rustyline::error::ReadlineError;
use rustyline::{Result as RustylineResult};
use rustyline::completion::{Completer, Pair};
use rustyline::highlight::Highlighter;
use rustyline::hint::Hinter;
use rustyline::validate::Validator;
use rustyline::Editor;
use crossterm::style::Color;
use regex::Regex;

#[derive(Serialize, Deserialize, Clone)]
struct CxConfig {
    #[serde(default = "default_debug")]
    pub debug: bool,
    #[serde(default = "default_chat")]
    pub default_chat: Option<u8>,
    #[serde(default = "default_auto_truncate")]
    pub auto_truncate: bool,
    #[serde(default = "default_truncate_length")]
    pub truncate_length: usize,
    #[serde(default = "default_rich_output")]
    pub rich_output: bool,
}

impl Default for CxConfig {
    fn default() -> Self {
        Self {
            debug: false,
            default_chat: None,
            auto_truncate: true,
            truncate_length: 8192, // 8KB default
            rich_output: true, // Enable rich output by default
        }
    }
}

fn default_debug() -> bool { false }
fn default_chat() -> Option<u8> { None }
fn default_auto_truncate() -> bool { true }
fn default_truncate_length() -> usize { 8192 }
fn default_rich_output() -> bool { true }

#[derive(Serialize)]
struct CxCommand {
    r#type: String,
    data: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    chat: Option<u8>,
    #[serde(skip_serializing_if = "Option::is_none")]
    format: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    supports_confirmations: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    confirmation_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    response: Option<String>,
}

#[derive(Deserialize)]
struct CxResponse {
    response: Option<String>,
    result: Option<String>,
    error: Option<String>,
    r#type: Option<String>,
    message: Option<String>,
    default: Option<String>,
    confirmation_id: Option<String>,
}

fn get_config_path() -> PathBuf {
    let home = env::var("HOME").unwrap_or_else(|_| ".".to_string());
    PathBuf::from(home).join(".calous").join("cx.json")
}

fn get_history_path() -> PathBuf {
    let home = env::var("HOME").unwrap_or_else(|_| ".".to_string());
    PathBuf::from(home).join(".calous").join("cx_history.txt")
}

fn get_commands_path() -> PathBuf {
    let home = env::var("HOME").unwrap_or_else(|_| ".".to_string());
    PathBuf::from(home).join(".calous").join("commands.txt")
}

fn load_commands() -> Vec<String> {
    let commands_path = get_commands_path();
    if commands_path.exists() {
        match fs::read_to_string(&commands_path) {
            Ok(content) => {
                content.lines()
                    .map(|line| line.trim().to_string())
                    .filter(|line| !line.is_empty())
                    .collect()
            }
            Err(_) => Vec::new(),
        }
    } else {
        Vec::new()
    }
}

fn load_config() -> CxConfig {
    let config_path = get_config_path();
    
    if config_path.exists() {
        match fs::read_to_string(&config_path) {
            Ok(content) => {
                match serde_json::from_str(&content) {
                    Ok(config) => config,
                    Err(e) => {
                        eprintln!("Warning: Failed to parse config file: {}", e);
                        CxConfig::default()
                    }
                }
            }
            Err(e) => {
                eprintln!("Warning: Failed to read config file: {}", e);
                CxConfig::default()
            }
        }
    } else {
        // Create default config file
        let config = CxConfig::default();
        save_config(&config);
        config
    }
}

fn save_config(config: &CxConfig) {
    let config_path = get_config_path();
    
    // Create .calous directory if it doesn't exist
    if let Some(parent) = config_path.parent() {
        if !parent.exists() {
            if let Err(e) = fs::create_dir_all(parent) {
                eprintln!("Warning: Failed to create config directory: {}", e);
                return;
            }
        }
    }
    
    match serde_json::to_string_pretty(config) {
        Ok(content) => {
            if let Err(e) = fs::write(&config_path, content) {
                eprintln!("Warning: Failed to write config file: {}", e);
            }
        }
        Err(e) => {
            eprintln!("Warning: Failed to serialize config: {}", e);
        }
    }
}

fn truncate_input(input: &str, max_length: usize) -> String {
    if input.len() <= max_length {
        input.to_string()
    } else {
        let truncated = &input[..max_length];
        format!("{}\n\n[... truncated {} bytes]", truncated, input.len() - max_length)
    }
}

#[derive(Clone)]
struct CommandCompleter {
    commands: Vec<String>,
}

impl CommandCompleter {
    fn new() -> Self {
        Self {
            commands: load_commands(),
        }
    }
}

impl Completer for CommandCompleter {
    type Candidate = Pair;

    fn complete(
        &self,
        line: &str,
        pos: usize,
        _ctx: &rustyline::Context<'_>,
    ) -> RustylineResult<(usize, Vec<Pair>)> {
        let start = line[..pos].rfind(' ').map_or(0, |i| i + 1);
        let prefix = &line[start..pos];
        
        if prefix.starts_with('/') || prefix.is_empty() {
            let search_prefix = if prefix.is_empty() { "/" } else { prefix };
            
            let matches: Vec<Pair> = self.commands
                .iter()
                .filter(|cmd| cmd.starts_with(search_prefix))
                .map(|cmd| Pair {
                    display: cmd.clone(),
                    replacement: cmd.clone(),
                })
                .collect();
            
            Ok((start, matches))
        } else {
            Ok((start, Vec::new()))
        }
    }
}

impl Hinter for CommandCompleter {
    type Hint = String;

    fn hint(&self, line: &str, pos: usize, _ctx: &rustyline::Context<'_>) -> Option<String> {
        if pos < line.len() {
            return None;
        }
        
        let start = line[..pos].rfind(' ').map_or(0, |i| i + 1);
        let prefix = &line[start..pos];
        
        if prefix.starts_with('/') {
            self.commands
                .iter()
                .find(|cmd| cmd.starts_with(prefix) && cmd.len() > prefix.len())
                .map(|cmd| cmd[prefix.len()..].to_string())
        } else {
            None
        }
    }
}

impl Highlighter for CommandCompleter {}

impl Validator for CommandCompleter {}

impl rustyline::Helper for CommandCompleter {}

fn parse_and_print_rich_text(text: &str, use_rich: bool) {
    if !use_rich {
        print!("{}", text);
        return;
    }

    // Process text line by line to handle end-of-line patterns
    let lines: Vec<&str> = text.lines().collect();
    let mut processed_lines = Vec::new();
    
    for line in lines {
        let mut processed_line = line.to_string();
        
        // Rich tag patterns
        let rich_patterns = [
            // Basic colors with full closing tags
            (r"\[red\](.*?)\[/red\]", Color::Red),
            (r"\[green\](.*?)\[/green\]", Color::Green),
            (r"\[blue\](.*?)\[/blue\]", Color::Blue),
            (r"\[yellow\](.*?)\[/yellow\]", Color::Yellow),
            (r"\[magenta\](.*?)\[/magenta\]", Color::Magenta),
            (r"\[cyan\](.*?)\[/cyan\]", Color::Cyan),
            (r"\[white\](.*?)\[/white\]", Color::White),
            (r"\[grey50\](.*?)\[/grey50\]", Color::DarkGrey),
            
            // Simple color closing tags with [/]
            (r"\[red\](.*?)\[/\]", Color::Red),
            (r"\[green\](.*?)\[/\]", Color::Green),
            (r"\[blue\](.*?)\[/\]", Color::Blue),
            (r"\[yellow\](.*?)\[/\]", Color::Yellow),
            (r"\[cyan\](.*?)\[/\]", Color::Cyan),
            (r"\[white\](.*?)\[/\]", Color::White),
            (r"\[grey50\](.*?)\[/\]", Color::DarkGrey),
            (r"\[magenta\](.*?)\[/\]", Color::Magenta),
            
            // Colors that continue to end of line (no explicit closing)
            (r"\[red\](.*?)$", Color::Red),
            (r"\[green\](.*?)$", Color::Green),
            (r"\[blue\](.*?)$", Color::Blue),
            (r"\[yellow\](.*?)$", Color::Yellow),
            (r"\[cyan\](.*?)$", Color::Cyan),
            (r"\[white\](.*?)$", Color::White),
            (r"\[grey50\](.*?)$", Color::DarkGrey),
            (r"\[magenta\](.*?)$", Color::Magenta),
        ];
        
        // Process each pattern
        for (pattern, color) in &rich_patterns {
            if let Ok(re) = Regex::new(pattern) {
                while let Some(cap) = re.captures(&processed_line) {
                    if let Some(matched_text) = cap.get(1) {
                        let replacement = format_with_color(matched_text.as_str(), *color);
                        processed_line = re.replace(&processed_line, replacement.as_str()).to_string();
                    } else {
                        break;
                    }
                }
            }
        }
        
        processed_lines.push(processed_line);
    }
    
    let mut output = processed_lines.join("\n");
    
    // Handle bold tags separately
    if let Ok(bold_re) = Regex::new(r"\[bold\](.*?)\[/bold\]") {
        while let Some(cap) = bold_re.captures(&output) {
            if let Some(matched_text) = cap.get(1) {
                let replacement = format_with_bold(matched_text.as_str());
                output = bold_re.replace(&output, replacement.as_str()).to_string();
            } else {
                break;
            }
        }
    }
    
    // Handle bold colors (patterns that use bold + color but render as just bold color)
    let bold_color_patterns = [
        (r"\[bold red\](.*?)\[/bold red\]", Color::Red),
        (r"\[bold green\](.*?)\[/bold green\]", Color::Green),
        (r"\[bold blue\](.*?)\[/bold blue\]", Color::Blue),
        (r"\[bold yellow\](.*?)\[/bold yellow\]", Color::Yellow),
        (r"\[bold cyan\](.*?)\[/bold cyan\]", Color::Cyan),
        (r"\[bold white\](.*?)\[/bold white\]", Color::White),
        (r"\[bold grey50\](.*?)\[/bold grey50\]", Color::DarkGrey),
        (r"\[bold magenta\](.*?)\[/bold magenta\]", Color::Magenta),
    ];
    
    for (pattern, color) in &bold_color_patterns {
        if let Ok(re) = Regex::new(pattern) {
            while let Some(cap) = re.captures(&output) {
                if let Some(matched_text) = cap.get(1) {
                    let replacement = format_with_bold_color(matched_text.as_str(), *color);
                    output = re.replace(&output, replacement.as_str()).to_string();
                } else {
                    break;
                }
            }
        }
    }
    
    print!("{}", output);
}

fn format_with_color(text: &str, color: Color) -> String {
    // We'll use ANSI escape codes directly since crossterm's execute! is for stdout
    let color_code = match color {
        Color::Red => "\x1b[31m",
        Color::Green => "\x1b[32m",
        Color::Blue => "\x1b[34m", 
        Color::Yellow => "\x1b[33m",
        Color::Magenta => "\x1b[35m",
        Color::Cyan => "\x1b[36m",
        Color::White => "\x1b[37m",
        Color::DarkGrey => "\x1b[90m",
        _ => "\x1b[0m",
    };
    format!("{}{}\x1b[0m", color_code, text)
}

fn format_with_bold(text: &str) -> String {
    format!("\x1b[1m{}\x1b[0m", text)
}

fn format_with_bold_color(text: &str, color: Color) -> String {
    let color_code = match color {
        Color::Red => "\x1b[1;31m",
        Color::Green => "\x1b[1;32m",
        Color::Blue => "\x1b[1;34m",
        Color::Yellow => "\x1b[1;33m",
        Color::Magenta => "\x1b[1;35m",
        Color::Cyan => "\x1b[1;36m",
        Color::White => "\x1b[1;37m",
        Color::DarkGrey => "\x1b[1;90m",
        _ => "\x1b[1m",
    };
    format!("{}{}\x1b[0m", color_code, text)
}

fn create_command(data: String, message_type: &str, chat: Option<u8>, rich_output: bool) -> CxCommand {
    let format_type = if rich_output { "rich" } else { "plain" };
    
    CxCommand {
        r#type: message_type.to_string(),
        data,
        chat,
        format: Some(format_type.to_string()),
        supports_confirmations: Some(true),
        confirmation_id: None,
        response: None,
    }
}

fn handle_server_response(response: &str, _debug: bool, rich_output: bool) -> Result<(), String> {
    let result: CxResponse = serde_json::from_str(response).unwrap_or(CxResponse {
        response: None,
        result: None,
        error: Some("Invalid response".to_string()),
        r#type: None,
        message: None,
        default: None,
        confirmation_id: None,
    });

    if let Some(err) = result.error {
        eprintln!("Error: {}", err);
    } else if let Some(res) = result.response {
        parse_and_print_rich_text(&res, rich_output);
    } else if let Some(res) = result.result {
        parse_and_print_rich_text(&res, rich_output);
    } else {
        println!("[No output]");
    }
    
    Ok(())
}

fn main() {
    let args: Vec<String> = env::args().collect();
    
    // Load configuration
    let config = load_config();
    
    // Parse flags
    let mut debug = config.debug;
    let mut chat_channel: Option<u8> = config.default_chat;
    let mut no_truncate = false;  // Temporary override for this command only
    let mut rich_output = config.rich_output;  // Rich output override
    let mut arg_start = 1;
    
    // Handle flags and special commands
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "-h" | "--help" => {
                println!("cx - CALOUS client");
                println!();
                println!("USAGE:");
                println!("    cx [OPTIONS] [text]");
                println!("    cx [OPTIONS] -c <command> [args...]");
                println!("    echo 'text' | cx [OPTIONS]");
                println!();
                println!("OPTIONS:");
                println!("    -c, --cmd          Send command instead of prompt");
                println!("    -d, --debug        Show debug output");
                println!("    -h, --help         Show this help message");
                println!("    -i, --interactive  Start interactive mode");
                println!("    -n, --chat <NUM>   Switch to chat channel (1-14)");
                println!("    -r, --rich         Enable rich text output");
                println!("    -p, --plain        Disable rich text output (plain text only)");
                println!("    -t, --no-truncate  Disable truncation for this command");
                println!("    -v, --version      Show version");
                println!();
                println!("EXAMPLES:");
                println!("    cx What is Rust?");
                println!("    cx Hello, world!");
                println!("    cx -c sys.help                 # Show server commands");
                println!("    cx -n 2 How are you?           # Send to chat channel 2");
                println!("    cx -n 3 -c chat.vars           # Show variables for chat 3");
                println!("    cat file.txt | cx What's in this file?");
                println!("    cat largefile.txt | cx -t Analyze this # No truncation");
                std::process::exit(0);
            }
            "-v" | "--version" => {
                println!("cx {}", env!("CARGO_PKG_VERSION"));
                std::process::exit(0);
            }
            "-d" | "--debug" => {
                debug = true;
                i += 1;
            }
            "-t" | "--no-truncate" => {
                no_truncate = true;
                i += 1;
            }
            "-r" | "--rich" => {
                rich_output = true;
                i += 1;
            }
            "-p" | "--plain" => {
                rich_output = false;
                i += 1;
            }
            "-i" | "--interactive" => {
                let mut config_with_rich = config.clone();
                config_with_rich.rich_output = rich_output;
                interactive_mode(debug, &config_with_rich);
                std::process::exit(0);
            }
            "-n" | "--chat" => {
                if i + 1 >= args.len() {
                    eprintln!("Error: -n flag requires a chat number (1-14)");
                    std::process::exit(1);
                }
                match args[i + 1].parse::<u8>() {
                    Ok(n) if n >= 1 && n <= 14 => {
                        chat_channel = Some(n);
                        i += 2;
                    }
                    _ => {
                        eprintln!("Error: Invalid chat number '{}'. Must be 1-14.", args[i + 1]);
                        std::process::exit(1);
                    }
                }
            }
            _ => {
                arg_start = i;
                break;
            }
        }
    }
    
    if debug {
        eprintln!("[Debug] Args: {:?}", args);
    }
    
    let prompt = if args.len() >= arg_start + 1 {
        // Command line arguments provided - use them regardless of stdin status
        if args[arg_start] == "-c" || args[arg_start] == "--cmd" {
            if args.len() < arg_start + 2 {
                eprintln!("Error: -c flag requires a command");
                std::process::exit(1);
            }
            // Join command and all its arguments
            let cmd_parts: Vec<String> = args[arg_start + 1..].to_vec();
            if cmd_parts[0].starts_with('/') {
                cmd_parts.join(" ")
            } else {
                format!("/{}", cmd_parts.join(" "))
            }
        } else {
            // Regular prompt from args - join ALL remaining arguments
            let prompt_text = args[arg_start..].join(" ");
            
            // Check if it looks like an unrecognized flag (only check first arg)
            if args[arg_start].starts_with('-') {
                eprintln!("Error: Unrecognized flag '{}'", args[arg_start]);
                eprintln!("Try 'cx --help' for available options.");
                std::process::exit(1);
            }
            
            // If stdin has data and this is a text prompt, append stdin content
            if !atty::is(atty::Stream::Stdin) && !prompt_text.is_empty() {
                let mut stdin_content = String::new();
                io::stdin().read_to_string(&mut stdin_content).unwrap();
                let stdin_content = stdin_content.trim();
                if !stdin_content.is_empty() {
                    // Apply truncation to stdin content if enabled and not overridden
                    let final_stdin = if config.auto_truncate && !no_truncate && stdin_content.len() > config.truncate_length {
                        if debug {
                            eprintln!("[Debug] Truncating stdin from {} to {} bytes", stdin_content.len(), config.truncate_length);
                        }
                        truncate_input(stdin_content, config.truncate_length)
                    } else {
                        if debug && no_truncate && stdin_content.len() > config.truncate_length {
                            eprintln!("[Debug] Truncation disabled by --no-truncate flag (stdin: {} bytes)", stdin_content.len());
                        }
                        stdin_content.to_string()
                    };
                    format!("{}\n\n{}", prompt_text, final_stdin)
                } else {
                    prompt_text
                }
            } else {
                prompt_text
            }
        }
    } else if !atty::is(atty::Stream::Stdin) {
        // No command line args but stdin has data - read from stdin
        let mut buf = String::new();
        io::stdin().read_to_string(&mut buf).unwrap();
        let stdin_data = buf.trim();
        
        // Apply truncation to stdin-only data if enabled and not overridden
        if config.auto_truncate && !no_truncate && stdin_data.len() > config.truncate_length {
            if debug {
                eprintln!("[Debug] Truncating stdin-only input from {} to {} bytes", stdin_data.len(), config.truncate_length);
            }
            truncate_input(stdin_data, config.truncate_length)
        } else {
            if debug && no_truncate && stdin_data.len() > config.truncate_length {
                eprintln!("[Debug] Truncation disabled by --no-truncate flag (stdin-only: {} bytes)", stdin_data.len());
            }
            stdin_data.to_string()
        }
    } else {
        // No args and no stdin data
        eprintln!("Usage: cx [text] | cx -c <command> [args...] | echo 'text' | cx");
        eprintln!("Try 'cx --help' for more information.");
        std::process::exit(1)
    };

    if prompt.is_empty() {
        eprintln!("Empty input");
        std::process::exit(1);
    }

    // Chat channel targeting will be handled via protocol
    if let Some(channel) = chat_channel {
        if debug {
            eprintln!("[Debug] Targeting chat channel {}", channel);
        }
    }

    let message_type = if prompt.starts_with("/") { "cmd" } else { "prompt" };

    let data = if message_type == "cmd" {
        serde_json::json!({"action": prompt}).to_string()
    } else {
        prompt
    };

    let mut config_with_rich = config.clone();
    config_with_rich.rich_output = rich_output;
    
    let cmd = create_command(data, &message_type, chat_channel, rich_output);

    match send_command(&cmd, debug, &config_with_rich) {
        Ok(response) => {
            let _ = handle_server_response(&response, debug, rich_output);
        }
        Err(e) => {
            eprintln!("Error: {}", e);
            std::process::exit(1);
        }
    }
}

fn send_command(cmd: &CxCommand, debug: bool, _config: &CxConfig) -> Result<String, String> {
    let socket_path = "/tmp/calous.sock";
    let mut stream = UnixStream::connect(socket_path)
        .map_err(|e| format!("Failed to connect to socket: {}", e))?;
    
    let request = serde_json::to_string(cmd)
        .map_err(|e| format!("Failed to serialize request: {}", e))?;
    
    if debug {
        eprintln!("[Debug] Sending request: {}", request);
        eprintln!("[Debug] Request size: {} bytes", request.len());
    }
    
    stream.write_all(request.as_bytes())
        .map_err(|e| format!("Failed to write to socket: {}", e))?;

    // Read response in chunks to handle potential confirmation flow
    let mut response = String::new();
    let mut buffer = [0; 4096];
    
    loop {
        match stream.read(&mut buffer) {
            Ok(0) => break, // EOF
            Ok(n) => {
                let chunk = String::from_utf8_lossy(&buffer[..n]);
                response.push_str(&chunk);
                
                // Try to parse what we have so far
                if let Ok(parsed) = serde_json::from_str::<CxResponse>(&response) {
                    if let Some(msg_type) = &parsed.r#type {
                        if msg_type == "confirmation_request" {
                            if let (Some(message), Some(confirmation_id), Some(default)) = 
                                (&parsed.message, &parsed.confirmation_id, &parsed.default) {
                                
                                if debug {
                                    eprintln!("[Debug] Received confirmation request: {}", response);
                                }
                                
                                // Prompt user for confirmation
                                print!("{} [{}]: ", message, default);
                                io::stdout().flush().unwrap();
                                
                                let mut user_input = String::new();
                                io::stdin().read_line(&mut user_input).unwrap();
                                let user_input = user_input.trim();
                                
                                // Use default if empty, otherwise use user input
                                let response_value = if user_input.is_empty() {
                                    default.clone()
                                } else {
                                    user_input.to_string()
                                };
                                
                                // Send confirmation response back on the SAME socket connection
                                let confirmation_cmd = CxCommand {
                                    r#type: "confirmation_response".to_string(),
                                    data: "".to_string(),
                                    chat: None,
                                    format: None,
                                    supports_confirmations: None,
                                    confirmation_id: Some(confirmation_id.clone()),
                                    response: Some(response_value),
                                };
                                
                                let confirmation_request = serde_json::to_string(&confirmation_cmd)
                                    .map_err(|e| format!("Failed to serialize confirmation: {}", e))?;
                                
                                if debug {
                                    eprintln!("[Debug] Sending confirmation: {}", confirmation_request);
                                }
                                
                                // Write confirmation response to the same stream
                                stream.write_all(confirmation_request.as_bytes())
                                    .map_err(|e| format!("Failed to write confirmation: {}", e))?;
                                
                                // Clear response buffer and continue reading final response
                                response.clear();
                                continue;
                            }
                        } else {
                            // Got a complete non-confirmation response
                            break;
                        }
                    } else {
                        // Got a complete response without type
                        break;
                    }
                }
                // Continue reading if we don't have a complete JSON yet
            }
            Err(e) => return Err(format!("Failed to read from socket: {}", e)),
        }
    }
    
    if debug {
        eprintln!("[Debug] Final response: {}", response);
    }

    Ok(response)
}

fn interactive_mode(debug: bool, config: &CxConfig) {
    println!("CALOUS Interactive Mode");
    println!("Type 'quit' or 'exit' to leave, '/help' for commands");
    println!("Tab completion available for commands");
    println!();
    
    let mut rl = match Editor::new() {
        Ok(mut editor) => {
            // Set up completion
            let completer = CommandCompleter::new();
            editor.set_helper(Some(completer));
            editor
        },
        Err(e) => {
            eprintln!("Warning: Failed to initialize readline: {}", e);
            eprintln!("Falling back to basic input mode");
            interactive_mode_basic(debug, config);
            return;
        }
    };
    
    let history_path = get_history_path();
    
    // Load history if file exists
    if history_path.exists() {
        if let Err(e) = rl.load_history(&history_path) {
            if debug {
                eprintln!("[Debug] Failed to load history: {}", e);
            }
        }
    }
    
    loop {
        let readline = rl.readline("> ");
        match readline {
            Ok(line) => {
                let input = line.trim();
                
                if input.is_empty() {
                    continue;
                }
                
                if input == "quit" || input == "exit" {
                    println!("Goodbye!");
                    break;
                }
                
                // Add to history
                rl.add_history_entry(input).unwrap_or_default();
                
                // Send the input to the server
                send_to_server(input, debug, config);
                println!();
            }
            Err(ReadlineError::Interrupted) => {
                println!("^C");
                continue;
            }
            Err(ReadlineError::Eof) => {
                println!("^D");
                break;
            }
            Err(err) => {
                eprintln!("Error: {:?}", err);
                break;
            }
        }
    }
    
    // Save history
    if let Err(e) = rl.save_history(&history_path) {
        if debug {
            eprintln!("[Debug] Failed to save history: {}", e);
        }
    }
}

fn interactive_mode_basic(debug: bool, config: &CxConfig) {
    loop {
        print!("> ");
        io::stdout().flush().unwrap();
        
        let mut input = String::new();
        match io::stdin().read_line(&mut input) {
            Ok(_) => {
                let input = input.trim();
                
                if input.is_empty() {
                    continue;
                }
                
                if input == "quit" || input == "exit" {
                    println!("Goodbye!");
                    break;
                }
                
                // Send the input to the server
                send_to_server(input, debug, config);
                println!();
            }
            Err(error) => {
                eprintln!("Error reading input: {}", error);
                break;
            }
        }
    }
}

fn send_to_server(input: &str, debug: bool, config: &CxConfig) {
    let message_type = if input.starts_with("/") { "cmd" } else { "prompt" };

    let data = if message_type == "cmd" {
        serde_json::json!({"action": input}).to_string()
    } else {
        input.to_string()
    };

    let cmd = create_command(data, &message_type, None, config.rich_output);

    match send_command(&cmd, debug, &config) {
        Ok(response) => {
            let _ = handle_server_response(&response, debug, config.rich_output);
        }
        Err(e) => {
            eprintln!("Error: {}", e);
        }
    }
}
