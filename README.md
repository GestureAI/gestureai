# GestureAI

**GestureAI** is a real-time chat platform built for accessibility and innovation. It allows users to communicate via standard text and image sharing, but its core feature is an integrated AI model that interprets American Sign Language (ASL) gestures from a webcam feed and converts them into text input in real-time.

This project was developed as our final apprenticeship project ("Svenneprøve").

## Preview

### Main page light mode  
![Overview](docs/overview_light.png)

### Main page dark mode  
![Coin view](docs/overview_dark.png)

### AI ASL feature  
![Coin view](docs/asl.png)

## Features

*   **Real-time Messaging:** Instant chat functionality with other online users.
*   **ASL Recognition:** Toggle your webcam to translate ASL hand signs into text characters using a custom Python AI model.
*   **Media Sharing:** Upload and share images within the chat.
*   **Modern UI:** Clean, responsive interface built with TailwindCSS and shadcn-svelte.
*   **Containerized:** Fully dockerized for easy deployment.

## Tech Stack

**Frontend & Backend Logic:**
*   Svelte & SvelteKit
*   TypeScript
*   TailwindCSS
*   shadcn-svelte
*   WebSocket (Real-time communication)

**AI & Analytics:**
*   Python (ASL Recognition Model & Analytics)

**Infrastructure:**
*   Docker & Docker Compose

## Usage

1.  **Sign In/Join:** Enter a username to join the global chat.
2.  **Chat:** Type normally or upload images using the attachment icon.
3.  **Gesture Mode:** Click the **Camera** icon to enable Gesture Mode.
    *   Grant webcam permissions.
    *   Perform ASL signs clearly in front of the camera.
    *   The recognized characters will appear in your input field automatically.

## License

Distributed under the MIT License. See `LICENSE` for more information.
