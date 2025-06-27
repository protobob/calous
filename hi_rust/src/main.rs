use std::env;
use std::io::{self, Read, Write};
use std::os::unix::net::UnixStream;

use serde::{Deserialize, Serialize};

#[derive(Serialize)]
struct HiCommand {
    r#type: String,
    data: String,
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
    let mut arg_start = 1;
    
    // Handle flags and special commands
    if args.len() >= 2 {
        match args[1].as_str() {
            "-h" | "--help" => {
                println!("hi - HiOllama client");
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
                println!("    -v, --version      Show version");
                println!();
                println!("EXAMPLES:");
                println!("    hi \"What is Rust?\"");
                println!("    hi -c sys.help");
                println!("    hi -c persona.set 0 You are a helpful assistant");
                println!("    cat file.txt | hi \"What's in this file?\"");
                std::process::exit(0);
            }
            "-v" | "--version" => {
                println!("hi 0.1.0");
                std::process::exit(0);
            }
            "-d" | "--debug" => {
                debug = true;
                arg_start = 2;
            }
            "-i" | "--interactive" => {
                interactive_mode(debug);
                std::process::exit(0);
            }
            _ => {}
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
            // Regular prompt from args
            let prompt_text = args[arg_start..].join(" ");
            
            // Check if it looks like an unrecognized flag
            if prompt_text.starts_with('-') {
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

    let message_type = if prompt.starts_with("/") { "cmd" } else { "prompt" };

    let data = if message_type == "cmd" {
        serde_json::json!({"action": prompt}).to_string()
    } else {
        prompt
    };

    let cmd = HiCommand {
        r#type: message_type.to_string(),
        data,
    };

    let socket_path = "/tmp/hiollama.sock";
    let mut stream = match UnixStream::connect(socket_path) {
        Ok(stream) => stream,
        Err(e) => {
            eprintln!("Error: Failed to connect to socket: {}", e);
            std::process::exit(1);
        }
    };
    
    let request = serde_json::to_string(&cmd).expect("Failed to serialize request");
    
    if debug {
        eprintln!("[Debug] Sending request: {}", request);
        eprintln!("[Debug] Request size: {} bytes", request.len());
    }
    
    if let Err(e) = stream.write_all(request.as_bytes()) {
        eprintln!("Error: Failed to write to socket: {}", e);
        std::process::exit(1);
    }

    let mut response = String::new();
    if let Err(e) = stream.read_to_string(&mut response) {
        eprintln!("Error: Failed to read from socket: {}", e);
        std::process::exit(1);
    }
    
    if debug {
        eprintln!("[Debug] Received response: {}", response);
    }

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

fn interactive_mode(debug: bool) {
    println!("HiOllama Interactive Mode");
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
    };

    let socket_path = "/tmp/hiollama.sock";
    
    let mut stream = match UnixStream::connect(socket_path) {
        Ok(stream) => stream,
        Err(e) => {
            eprintln!("Error: Failed to connect to socket: {}", e);
            return;
        }
    };
    
    let request = serde_json::to_string(&cmd).expect("Failed to serialize request");
    
    if debug {
        eprintln!("[Debug] Sending request: {}", request);
    }
    
    if let Err(e) = stream.write_all(request.as_bytes()) {
        eprintln!("Error: Failed to write to socket: {}", e);
        return;
    }

    let mut response = String::new();
    if let Err(e) = stream.read_to_string(&mut response) {
        eprintln!("Error: Failed to read from socket: {}", e);
        return;
    }
    
    if debug {
        eprintln!("[Debug] Received response: {}", response);
    }

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
