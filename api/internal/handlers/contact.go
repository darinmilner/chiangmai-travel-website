package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

	"api/internal/config"
	"api/internal/models"

	"github.com/gin-gonic/gin"
)

// ContactForm handles the contact form submission
func ContactForm(c *gin.Context) {
	var req models.ContactRequest

	// Parse JSON request
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ContactResponse{
			Success: false,
			Message: "Invalid request format",
		})
		return
	}

	// Check honeypot
	if req.Website != "" {
		c.JSON(http.StatusOK, models.ContactResponse{
			Success: true,
			Message: "Thank you for your message! We'll get back to you soon.",
		})
		return
	}

	// Validate required fields
	if req.Name == "" || req.Email == "" || req.Subject == "" || req.Message == "" {
		c.JSON(http.StatusBadRequest, models.ContactResponse{
			Success: false,
			Message: "All fields except phone are required",
		})
		return
	}

	// Get contact configuration
	config, err := getContactConfig()
	if err != nil {
		log.Printf("❌ Error loading config: %v", err)
		c.JSON(http.StatusInternalServerError, models.ContactResponse{
			Success: false,
			Message: "Unable to send message. Please try again later.",
		})
		return
	}

	// Send to Lambda via API Gateway
	if err := sendToLambda(req, config.Contact.APIURL); err != nil {
		log.Printf("❌ Error sending to Lambda: %v", err)
		c.JSON(http.StatusInternalServerError, models.ContactResponse{
			Success: false,
			Message: "Unable to send message. Please try again later.",
		})
		return
	}

	c.JSON(http.StatusOK, models.ContactResponse{
		Success: true,
		Message: "Thank you for your message! We'll get back to you within 24 hours.",
	})
}

// getContactConfig loads contact configuration
func getContactConfig() (*config.AppConfig, error) {
	// Load from environment
	appConfig := config.LoadFullConfig()
	if appConfig == nil {
		return nil, fmt.Errorf("failed to load config")
	}

	log.Printf("📧 Contact config loaded: recipient=%s", appConfig.Contact.RecipientEmail)

	return appConfig, nil
}

// sendToLambda sends the contact data to AWS Lambda via API Gateway
func sendToLambda(req models.ContactRequest, apiURL string) error {
	// If no API URL is provided, log the message (development mode)
	if apiURL == "" {
		log.Printf("📧 Contact message (dev mode):")
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
		return fmt.Errorf("failed to marshal contact request: %w", err)
	}

	// Create HTTP client with timeout
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	// Create request
	httpReq, err := http.NewRequest("POST", apiURL, bytes.NewBuffer(body))
	if err != nil {
		return fmt.Errorf("failed to create HTTP request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")

	// Send request
	resp, err := client.Do(httpReq)
	if err != nil {
		return fmt.Errorf("failed to dispatch request to API Gateway: %w", err)
	}
	defer resp.Body.Close()

	// Check response status range (200-299)
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		respBody, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("API Gateway returned status %d: %s", resp.StatusCode, string(respBody))
	}

	return nil
}
