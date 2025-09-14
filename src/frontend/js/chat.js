// This file contains the logic for communicating with the ChillBuddy backend.

/**
 * Sends a message to the ChillBuddy backend and returns the response.
 * @param {string} userMessage The message from the user.
 * @param {Array} conversationHistory Optional conversation history.
 * @returns {Promise<string>} The text response from ChillBuddy.
 */
async function getChillBuddyResponse(userMessage, conversationHistory = []) {
  // Use the backend API URL from config
  const url = `${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.CHAT}`;

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        // Add any auth headers if needed
      },
      body: JSON.stringify({ 
        message: userMessage,
        conversation_history: conversationHistory 
      }),
    });

    // Check if the response from the backend was successful
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`ChillBuddy backend error: ${response.status} ${response.statusText}`, errorText);
      
      if (response.status === 401) {
        return "I need you to be authenticated to chat. Please refresh the page and try again.";
      } else if (response.status === 429) {
        return "You're sending messages too quickly. Please take a moment and try again.";
      } else if (response.status >= 500) {
        return "I'm experiencing some technical difficulties. Please try again in a moment.";
      }
      
      return "I'm sorry, but I couldn't process your message right now. Please try again.";
    }
    
    const data = await response.json();

    // Check for the expected response structure from ChillBuddy backend
    if (data && data.message) {
      return data.message;
    }

    // Handle crisis detection
    if (data && data.crisis_detected) {
      return data.message || "I'm here to support you. If you're in crisis, please reach out to a mental health professional or crisis hotline.";
    }

    // If the structure is not as expected, log it and return a graceful error message
    console.error("Invalid response structure from ChillBuddy backend:", data);
    return "I'm having a little trouble thinking right now. Could you try rephrasing your message?";
  } catch (error) {
    console.error("ChillBuddy Backend Error:", error);
    return "I'm having a little trouble connecting right now. Please try again in a moment.";
  }
}

