const express = require("express");
const { google } = require("googleapis");
const dotenv = require("dotenv");
const cors = require("cors");
const cookieParser = require("cookie-parser");
const fs = require("fs");

dotenv.config();

const app = express();
app.use(cors());
app.use(cookieParser());
app.use(express.json());

const SCOPES = ["https://www.googleapis.com/auth/gmail.send"];

const CLIENT_ID = process.env.CLIENT_ID;
const CLIENT_SECRET = process.env.CLIENT_SECRET;
const REDIRECT_URI = process.env.REDIRECT_URI;

const oauth2Client = new google.auth.OAuth2(
  CLIENT_ID,
  CLIENT_SECRET,
  REDIRECT_URI
);

// Load AI-generated content dynamically (Placeholder for ChatGPT API)
const getAIContent = async () => {
  return {
    subject: "Your AI-Generated Job Application",
    body: "Dear Hiring Manager,\n\nI am excited to apply for the position...\n\nBest regards,\nJohn Doe",
    recipient: "employer@example.com", // Placeholder
  };
};

// Step 1: Redirect user to Google OAuth login
app.get("/auth", (req, res) => {
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: "offline",
    scope: SCOPES,
  });
  res.redirect(authUrl);
});

// Step 2: Google OAuth Callback
app.get("/auth/callback", async (req, res) => {
  const code = req.query.code;
  if (!code) return res.status(400).send("No code received.");

  try {
    const { tokens } = await oauth2Client.getToken(code);
    oauth2Client.setCredentials(tokens);

    // Save token in cookies (or DB for persistent login)
    res.cookie("gmail_token", tokens.refresh_token, { httpOnly: true });

    // Redirect to a placeholder loading page
    res.redirect("https://yourwebsite.com/loading"); // Replace with your actual URL
  } catch (error) {
    console.error("Error getting token:", error);
    res.status(500).send("Authentication failed");
  }
});

// Step 3: Send Email
app.post("/send-email", async (req, res) => {
  try {
    // Get AI-generated content (Replace with ChatGPT API integration)
    const aiContent = await getAIContent();
    const { subject, body, recipient } = aiContent;

    // Retrieve user token from cookies
    const token = req.cookies.gmail_token;
    if (!token) return res.status(401).send("Unauthorized");

    oauth2Client.setCredentials({ refresh_token: token });

    const gmail = google.gmail({ version: "v1", auth: oauth2Client });

    // Create email body
    const email = [
      `To: ${recipient}`,
      "Content-Type: text/plain; charset=\"UTF-8\"",
      "MIME-Version: 1.0",
      `Subject: ${subject}`,
      "",
      body,
    ].join("\n");

    const encodedEmail = Buffer.from(email).toString("base64").replace(/\+/g, "-").replace(/\//g, "_");

    await gmail.users.messages.send({
      userId: "me",
      requestBody: {
        raw: encodedEmail,
      },
    });

    res.json({ success: true, message: "Email sent successfully" });
  } catch (error) {
    console.error("Error sending email:", error);
    res.status(500).json({ success: false, message: "Email send failed" });
  }
});

// Server Listen
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
