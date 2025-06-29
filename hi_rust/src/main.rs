use std::env;
use std::io::{self, Read, Write};
use std::os::unix::net::UnixStream;

use serde::{Deserialize, Serialize};

#[derive(Serialize)]
struct HiCommand {
    r#type: String,
    data: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    chat: Option<u8>,
}

#[derive(Deserialize)]
struct HiResponse {
    response: Option<String>,
    result: Option<String>,
    error: Option<String>,
}

fn main() {
    let args: Vec<String> = env::args().collect();
    
    // Parse flags
    let mut debug = false;
    let mut chat_channel: Option<u8> = None;
    let mut arg_start = 1;
    
    // Handle flags and special commands
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "-h" | "--help" => {
                println!("cx - CALOUS client");
                println!();
                println!("USAGE:");
                println!("    hi [OPTIONS] [text]");
                println!("    hi [OPTIONS] -c <command> [args...]");
                println!("    echo 'text' | hi [OPTIONS]");
                println!();
                println!("OPTIONS:");
                println!("    -c, --cmd          Send command instead of prompt");
                println!("    -d, --debug        Show debug output");
                println!("    -h, --help         Show this help message");
                println!("    -i, --interactive  Start interactive mode");
                println!("    -n, --chat <NUM>   Switch to chat channel (1-14)");
                println!("    -v, --version      Show version");
                println!();
                println!("EXAMPLES:");
                println!("    hi What is Rust?");
                println!("    hi Hello, world!");
                println!("    hi -c sys.help");
                println!("    hi -c persona.set 0 You are a helpful assistant");
                println!("    hi -n 2 How are you?           # Send to chat channel 2");
                println!("    hi -n 3 -c chat.vars           # Show variables for chat 3");
                println!("    cat file.txt | hi What's in this file?");
                println!();
                println!("CHAT COMMANDS:");
                println!("    hi -c chat.switch 2            # Switch to chat 2");
                println!("    hi -c chat.add                 # Add new chat");
                println!("    hi -c chat.vars                # Show chat variables");
                println!("    hi -c model.switch             # Change model");
                std::process::exit(0);
            }
            "-v" | "--version" => {
                println!("hi 0.1.0");
                std::process::exit(0);
            }
            "-d" | "--debug" => {
                debug = true;
                i += 1;
            }
            "-i" | "--interactive" => {
                interactive_mode(debug);
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
                eprintln!("Try 'hi --help' for available options.");
                std::process::exit(1);
            }
            
            // If stdin has data and this is a text prompt, append stdin content
            if !atty::is(atty::Stream::Stdin) && !prompt_text.is_empty() {
                let mut stdin_content = String::new();
                io::stdin().read_to_string(&mut stdin_content).unwrap();
                let stdin_content = stdin_content.trim();
                if !stdin_content.is_empty() {
                    format!("{}\n\n{}", prompt_text, stdin_content)
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
        buf.trim().to_string()
    } else {
        // No args and no stdin data
        eprintln!("Usage: hi [text] | hi -c <command> [args...] | echo 'text' | hi");
        eprintln!("Try 'hi --help' for more information.");
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

fn interactive_mode(debug: bool) {
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
                send_to_server(input, debug);
                println!();
            }
            Err(error) => {
                eprintln!("Error reading input: {}", error);
                break;
            }
        }
    }
}

fn send_to_server(input: &str, debug: bool) {
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
