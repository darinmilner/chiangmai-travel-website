package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
)

type ContactRequest struct {
	Name    string `json:"name"`
	Email   string `json:"email"`
	Phone   string `json:"phone"`
	Subject string `json:"subject"`
	Message string `json:"message"`
	Website string `json:"website"` // Honeypot
}

type ContactResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
}

// ContactForm handles the contact form submission
func ContactForm(c *gin.Context) {
	var req ContactRequest

	// Parse JSON request
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ContactResponse{
			Success: false,
			Message: "Invalid request format",
		})
		return
	}

	// Check honeypot
	if req.Website != "" {
		// Silently succeed - likely a bot
		c.JSON(http.StatusOK, ContactResponse{
			Success: true,
			Message: "Thank you for your message! We'll get back to you soon.",
		})
		return
	}

	// Validate required fields
	if req.Name == "" || req.Email == "" || req.Subject == "" || req.Message == "" {
		c.JSON(http.StatusBadRequest, ContactResponse{
			Success: false,
			Message: "All fields except phone are required",
		})
		return
	}

	// Send to Lambda via API Gateway
	if err := sendToLambda(req); err != nil {
		log.Printf("❌ Error sending to Lambda: %v", err)
		c.JSON(http.StatusInternalServerError, ContactResponse{
			Success: false,
			Message: "Unable to send message. Please try again later.",
		})
		return
	}

	c.JSON(http.StatusOK, ContactResponse{
		Success: true,
		Message: "Thank you for your message! We'll get back to you within 24 hours.",
	})
}

// sendToLambda sends the contact data to AWS Lambda via API Gateway
func sendToLambda(req ContactRequest) error {
	// Get API Gateway URL from environment
	apiURL := os.Getenv("CONTACT_API_URL")
	if apiURL == "" {
		// Fallback for development - log the message
		log.Printf("📧 Contact message (dev mode):\n")
		log.Printf("   Name: %s", req.Name)
		log.Printf("   Email: %s", req.Email)
		log.Printf("   Phone: %s", req.Phone)
		log.Printf("   Subject: %s", req.Subject)
		log.Printf("   Message: %s", req.Message)
		return nil
	}

	// Prepare request body
	body, err := json.Marshal(req)
	if err != nil {
		return err
	}

	// Create HTTP client with timeout
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	// Create request
	httpReq, err := http.NewRequest("POST", apiURL, bytes.NewBuffer(body))
	if err != nil {
		return err
	}
	httpReq.Header.Set("Content-Type", "application/json")

	// Send request
	resp, err := client.Do(httpReq)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	// Check response
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("lambda returned status: %d", resp.StatusCode)
	}

	return nil
}
