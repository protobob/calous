use std::env;
use std::io::{self, Read, Write};
use std::os::unix::net::UnixStream;
use std::fs;
use std::path::PathBuf;

use serde::{Deserialize, Serialize};

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
}

impl Default for CxConfig {
    fn default() -> Self {
        Self {
            debug: false,
            default_chat: None,
            auto_truncate: true,
            truncate_length: 8192, // 8KB default
        }
    }
}

fn default_debug() -> bool { false }
fn default_chat() -> Option<u8> { None }
fn default_auto_truncate() -> bool { true }
fn default_truncate_length() -> usize { 8192 }

#[derive(Serialize)]
struct HiCommand {
    r#type: String,
    data: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    chat: Option<u8>,
    #[serde(skip_serializing_if = "Option::is_none")]
    format: Option<String>,
}

#[derive(Deserialize)]
struct HiResponse {
    response: Option<String>,
    result: Option<String>,
    error: Option<String>,
}

fn get_config_path() -> PathBuf {
    let home = env::var("HOME").unwrap_or_else(|_| ".".to_string());
    PathBuf::from(home).join(".calous").join("cx.json")
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

fn main() {
    let args: Vec<String> = env::args().collect();
    
    // Load configuration
    let config = load_config();
    
    // Parse flags
    let mut debug = config.debug;
    let mut chat_channel: Option<u8> = config.default_chat;
    let mut no_truncate = false;  // Temporary override for this command only
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
            "-i" | "--interactive" => {
                interactive_mode(debug, &config);
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

    let cmd = HiCommand {
        r#type: message_type.to_string(),
        data,
        chat: chat_channel,
        format: Some("plain".to_string()),
    };

    match send_command(&cmd, debug) {
        Ok(response) => {
            let result: HiResponse = serde_json::from_str(&response).unwrap_or(HiResponse {
                response: None,
                result: None,
                error: Some("Invalid response".to_string()),
            });

            if let Some(err) = result.error {
                eprintln!("Error: {}", err);
            } else if let Some(res) = result.response {
                println!("{}", res);
            } else if let Some(res) = result.result {
                println!("{}", res);
            } else {
                println!("[No output]");
            }
        }
        Err(e) => {
            eprintln!("Error: {}", e);
            std::process::exit(1);
        }
    }
}

fn send_command(cmd: &HiCommand, debug: bool) -> Result<String, String> {
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

    let mut response = String::new();
    stream.read_to_string(&mut response)
        .map_err(|e| format!("Failed to read from socket: {}", e))?;
    
    if debug {
        eprintln!("[Debug] Received response: {}", response);
    }

    Ok(response)
}

fn interactive_mode(debug: bool, config: &CxConfig) {
    println!("CALOUS Interactive Mode");
    println!("Type 'quit' or 'exit' to leave, '/help' for commands");
    println!();
    
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

    let cmd = HiCommand {
        r#type: message_type.to_string(),
        data,
        chat: None,  // Interactive mode doesn't support chat targeting
        format: Some("plain".to_string()),
    };

    match send_command(&cmd, debug) {
        Ok(response) => {
            let result: HiResponse = serde_json::from_str(&response).unwrap_or(HiResponse {
                response: None,
                result: None,
                error: Some("Invalid response".to_string()),
            });

            if let Some(err) = result.error {
                eprintln!("Error: {}", err);
            } else if let Some(res) = result.response {
                println!("{}", res);
            } else if let Some(res) = result.result {
                println!("{}", res);
            } else {
                println!("[No output]");
            }
        }
        Err(e) => {
            eprintln!("Error: {}", e);
        }
    }
}
