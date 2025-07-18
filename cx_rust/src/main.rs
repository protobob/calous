use std::env;
use std::io::{self, Read, Write};
use std::os::unix::net::UnixStream;
use std::fs;
use std::path::PathBuf;
use std::sync::Mutex;

use serde::{Deserialize, Serialize};
use regex::Regex;
use rustyline::error::ReadlineError;
use rustyline::{Result as RustylineResult};
use rustyline::completion::{Completer, Pair};
use rustyline::highlight::Highlighter;
use rustyline::hint::Hinter;
use rustyline::validate::Validator;
use rustyline::Editor;

// Global status storage for REPL mode
static LAST_STATUS: Mutex<Option<serde_json::Value>> = Mutex::new(None);

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
    #[serde(default = "default_no_color")]
    pub no_color: bool,
}

impl Default for CxConfig {
    fn default() -> Self {
        Self {
            debug: false,
            default_chat: None,
            auto_truncate: true,
            truncate_length: 8192, // 8KB default
            no_color: false, // Show colors by default
        }
    }
}

fn default_debug() -> bool { false }
fn default_chat() -> Option<u8> { None }
fn default_auto_truncate() -> bool { true }
fn default_truncate_length() -> usize { 8192 }
fn default_no_color() -> bool { false }

#[derive(Serialize)]
struct CxCommand {
    r#type: String,
    data: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    chat: Option<u8>,
    #[serde(skip_serializing_if = "Option::is_none")]
    supports_confirmations: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    confirmation_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    response: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    repl_mode: Option<bool>,
}

// CxResponse struct removed - using delimiter protocol instead of JSON

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


fn strip_ansi_codes(text: &str) -> String {
    let ansi_regex = Regex::new(r"\x1B\[[0-?]*[ -/]*[@-~]").unwrap();
    ansi_regex.replace_all(text, "").to_string()
}

fn display_status(status: &serde_json::Value) {
    // Extract status fields with defaults
    let provider = status.get("provider").and_then(|v| v.as_str()).unwrap_or("unknown");
    let model = status.get("model").and_then(|v| v.as_str()).unwrap_or("none");
    let chat = status.get("chat").and_then(|v| v.as_u64()).unwrap_or(1);
    let history = status.get("history").and_then(|v| v.as_bool()).unwrap_or(true);
    
    let history_str = if history { "on" } else { "off" };
    
    // Use light blue color (96) for the status line
    print!("\x1b[96m[{} | {} | chat:{} | hist:{}]\x1b[0m\n", provider, model, chat, history_str);
}

fn show_status_before_prompt(_debug: bool, _config: &CxConfig) {
    // Display the last received status if we have one
    if let Ok(status_guard) = LAST_STATUS.lock() {
        if let Some(status) = status_guard.as_ref() {
            display_status(status);
        }
    }
}

fn create_command(data: String, message_type: &str, chat: Option<u8>, repl_mode: Option<bool>) -> CxCommand {
    CxCommand {
        r#type: message_type.to_string(),
        data,
        chat,
        supports_confirmations: Some(true),
        confirmation_id: None,
        response: None,
        repl_mode,
    }
}

fn handle_server_response(response: &str, _debug: bool, no_color: bool) -> Result<(), String> {
    // With delimiter protocol, response is just plain text
    // If response is empty, it means content was already printed during streaming
    if response.is_empty() {
        // Content was already printed during streaming, don't print anything else
        return Ok(());
    } else {
        let output = if no_color { strip_ansi_codes(response) } else { response.to_string() };
        println!("{}", output);
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
    let mut no_color = config.no_color;  // Color output override
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
                println!("    --test-repl        Test REPL mode status display");
                println!("    --no-color         Strip ANSI color codes from output");
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
                arg_start = i;
            }
            "-t" | "--no-truncate" => {
                no_truncate = true;
                i += 1;
                arg_start = i;
            }
            "--no-color" => {
                no_color = true;
                i += 1;
                arg_start = i;
            }
            "--test-repl" => {
                // Set flag for test REPL mode but continue processing
                i += 1;
                arg_start = i;  // Update arg_start to skip this flag
            }
            "-i" | "--interactive" => {
                let mut config_with_no_color = config.clone();
                config_with_no_color.no_color = no_color;
                interactive_mode(debug, &config_with_no_color);
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

    // With delimiter protocol, send raw command/prompt text
    let data = prompt;

    let mut config_with_no_color = config.clone();
    config_with_no_color.no_color = no_color;
    
    // Add a test flag to simulate REPL mode
    let is_repl_test = args.contains(&"--test-repl".to_string());
    let cmd = create_command(data, &message_type, chat_channel, if is_repl_test { Some(true) } else { None });

    match send_command(&cmd, debug, &config_with_no_color) {
        Ok(response) => {
            let _ = handle_server_response(&response, debug, no_color);
        }
        Err(e) => {
            eprintln!("Error: {}", e);
            std::process::exit(1);
        }
    }
}

fn send_command(cmd: &CxCommand, debug: bool, _config: &CxConfig) -> Result<String, String> {
    let is_repl_mode = cmd.repl_mode.unwrap_or(false);
    let socket_path = "/tmp/calous.sock";
    let mut stream = UnixStream::connect(socket_path)
        .map_err(|e| format!("Failed to connect to socket: {}", e))?;
    
    // Create delimiter-based request instead of JSON
    let request_type = if cmd.r#type == "cmd" { "CMD" } else { "PROMPT" };
    let escaped_data = cmd.data.replace('\0', "\0\0"); // Escape null bytes
    
    // Add REPL mode flag to request format if present
    let request = if cmd.repl_mode.unwrap_or(false) {
        format!("{}\0{}\0REPL\0END\0", request_type, escaped_data)
    } else {
        format!("{}\0{}\0END\0", request_type, escaped_data)
    };
    
    if debug {
        eprintln!("[Debug] Sending request: {} (length: {} bytes)", 
                  request.replace('\0', "\\0"), request.len());
    }
    
    stream.write_all(request.as_bytes())
        .map_err(|e| format!("Failed to write to socket: {}", e))?;

    // Read response using delimiter protocol
    let mut response = String::new();
    let mut buffer = [0; 4096];
    let mut has_printed_streaming = false;
    
    loop {
        match stream.read(&mut buffer) {
            Ok(0) => break, // EOF
            Ok(n) => {
                let chunk = String::from_utf8_lossy(&buffer[..n]);
                response.push_str(&chunk);
                
                // Print content immediately for streaming (simple approach)
                if !chunk.contains('\0') {
                    // No delimiters, just print the content immediately
                    if debug {
                        eprintln!("[Debug] Streaming chunk: {:?}", chunk);
                    }
                    print!("{}", chunk);
                    io::stdout().flush().unwrap();
                    has_printed_streaming = true;
                    continue; // Keep reading more
                }
                
                // Check for end delimiter
                if response.contains("\0END\0") {
                    // We have a complete response
                    if debug {
                        eprintln!("[Debug] Full response received: {:?}", response);
                    }
                    // Check if response contains status information
                    if response.contains("\0STATUS\0") {
                        // Status response: content\0STATUS\0{json}\0END\0
                        if debug {
                            eprintln!("[Debug] Received STATUS response");
                        }
                        if let Some(status_start) = response.find("\0STATUS\0") {
                            let status_json_start = status_start + 8; // Length of "\0STATUS\0"
                            if let Some(end_pos) = response.find("\0END\0") {
                                let status_json = &response[status_json_start..end_pos];
                                let unescaped_status = status_json.replace("\0\0", "\0");
                                
                                if debug {
                                    eprintln!("[Debug] Status JSON: {}", unescaped_status);
                                }
                                
                                // Parse and store status for display before next prompt
                                if let Ok(status) = serde_json::from_str::<serde_json::Value>(&unescaped_status) {
                                    // Store status for display before next prompt
                                    if let Ok(mut status_guard) = LAST_STATUS.lock() {
                                        *status_guard = Some(status);
                                    }
                                } else if debug {
                                    eprintln!("[Debug] Failed to parse status JSON");
                                }
                                
                                // If we already printed the content during streaming, return empty string
                                if has_printed_streaming {
                                    // Ensure a newline is printed after streaming content
                                    println!();
                                    return Ok(String::new());
                                } else {
                                    return Ok(String::new());
                                }
                            }
                        }
                    } else if response.starts_with("\0STATUS\0") {
                        // Pure status response: \0STATUS\0{json}\0END\0 (fallback)
                        if debug {
                            eprintln!("[Debug] Received pure STATUS response");
                        }
                        let status_start = 8; // Length of "\0STATUS\0"
                        if let Some(end_pos) = response.find("\0END\0") {
                            let status_json = &response[status_start..end_pos];
                            let unescaped_status = status_json.replace("\0\0", "\0");
                            
                            // Parse and store status for display before next prompt
                            if let Ok(status) = serde_json::from_str::<serde_json::Value>(&unescaped_status) {
                                if let Ok(mut status_guard) = LAST_STATUS.lock() {
                                    *status_guard = Some(status);
                                }
                            }
                            
                            return Ok(String::new());
                        }
                    } else if response.starts_with("\0ERROR\0") {
                        // Error response: \0ERROR\0{message}\0END\0
                        let error_start = 7; // Length of "\0ERROR\0"
                        if let Some(end_pos) = response.find("\0END\0") {
                            let error_msg = &response[error_start..end_pos];
                            let unescaped_msg = error_msg.replace("\0\0", "\0");
                            return Err(format!("Error: {}", unescaped_msg));
                        }
                    } else if response.starts_with("\0CONFIRM\0") {
                        // Confirmation request: \0CONFIRM\0{message}\0{default}\0{id}\0END\0
                        let parts: Vec<&str> = response.split('\0').collect();
                        if parts.len() >= 6 && parts[1] == "CONFIRM" && parts[5] == "END" {
                            let message = parts[2].replace("\0\0", "\0");
                            let default = parts[3].replace("\0\0", "\0");
                            let confirmation_id = parts[4];
                            
                            if debug {
                                eprintln!("[Debug] Received confirmation request: {}", message);
                            }
                            
                            // Prompt user for confirmation
                            print!("{} [{}]: ", message, default);
                            io::stdout().flush().unwrap();
                            
                            let mut user_input = String::new();
                            io::stdin().read_line(&mut user_input).unwrap();
                            let user_input = user_input.trim();
                            
                            // Use default if empty, otherwise use user input
                            let response_value = if user_input.is_empty() {
                                default
                            } else {
                                user_input.to_string()
                            };
                            
                            // Send confirmation response back on the same socket
                            let confirmation_response = format!(
                                "\0CONFIRM_RESPONSE\0{}\0{}\0END\0", 
                                confirmation_id, response_value
                            );
                            
                            if debug {
                                eprintln!("[Debug] Sending confirmation: {}", 
                                         confirmation_response.replace('\0', "\\0"));
                            }
                            
                            stream.write_all(confirmation_response.as_bytes())
                                .map_err(|e| format!("Failed to write confirmation: {}", e))?;
                            
                            // Clear response buffer and continue reading final response
                            response.clear();
                            continue;
                        }
                    } else {
                        // Normal response: {content}\0END\0
                        if let Some(end_pos) = response.find("\0END\0") {
                            let content = &response[..end_pos];
                            let unescaped_content = content.replace("\0\0", "\0");
                            
                            // If we already printed the content during streaming, return empty string
                            // to avoid duplicate output
                            if has_printed_streaming {
                                // Ensure a newline is printed after streaming content
                                println!();
                                return Ok(String::new());
                            } else {
                                return Ok(unescaped_content);
                            }
                        }
                    }
                    break;
                }
            }
            Err(e) => return Err(format!("Failed to read from socket: {}", e)),
        }
    }
    
    // If we get here, we didn't receive a complete response
    if response.is_empty() {
        Err("No response from server".to_string())
    } else {
        if debug {
            eprintln!("[Debug] Incomplete response: {}", response.replace('\0', "\\0"));
        }
        Err("Incomplete response from server".to_string())
    }
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
        // Show status before each prompt
        show_status_before_prompt(debug, config);
        
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

    // With delimiter protocol, send raw command/prompt text
    let data = input.to_string();

    let cmd = create_command(data, &message_type, None, Some(true));

    match send_command(&cmd, debug, &config) {
        Ok(response) => {
            let _ = handle_server_response(&response, debug, config.no_color);
        }
        Err(e) => {
            eprintln!("Error: {}", e);
        }
    }
}
