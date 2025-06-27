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
    let prompt = if atty::is(atty::Stream::Stdin) {
        // If run with args, use them
        env::args().skip(1).collect::<Vec<String>>().join(" ")
    } else {
        // Otherwise, read from stdin
        let mut buf = String::new();
        io::stdin().read_to_string(&mut buf).unwrap();
        buf.trim().to_string()
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
    let mut stream = UnixStream::connect(socket_path).expect("Failed to connect to socket");
    let request = serde_json::to_string(&cmd).expect("Failed to serialize request");
    println!("[Debug] Sending request: {}", request);
    stream.write_all(request.as_bytes()).expect("Failed to write to socket");

    let mut response = String::new();
    stream.read_to_string(&mut response).expect("Failed to read from socket");
    println!("[Debug] Received response: {}", response);

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
