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

func ContactForm(c *gin.Context) {
	var req models.ContactRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ContactResponse{
			Success: false,
			Message: "Invalid request payload",
		})
		return
	}

	// Honeypot check
	if req.Website != "" {
		c.JSON(http.StatusOK, models.ContactResponse{
			Success: true,
			Message: "Thank you for your message! We'll get back to you soon.",
		})
		return
	}

	if req.Name == "" || req.Email == "" || req.Subject == "" || req.Message == "" {
		c.JSON(http.StatusBadRequest, models.ContactResponse{
			Success: false,
			Message: "All fields except phone are required",
		})
		return
	}

	contactCfg := config.GetContactConfig()

	if err := sendToLambda(req, contactCfg.APIURL); err != nil {
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

func sendToLambda(req models.ContactRequest, apiURL string) error {
	if apiURL == "" {
		log.Printf("📧 Contact message (dev mode): From=%s <%s> | Subject=%s", req.Name, req.Email, req.Subject)
		return nil
	}

	payload := map[string]interface{}{
		"type":    "contact_response", // Matches SESProcessor routing
		"name":    req.Name,
		"email":   req.Email,
		"phone":   req.Phone,
		"subject": req.Subject,
		"message": req.Message,
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("failed to marshal payload: %w", err)
	}

	client := &http.Client{Timeout: 10 * time.Second}
	httpReq, err := http.NewRequest("POST", apiURL, bytes.NewBuffer(body))
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(httpReq)
	if err != nil {
		return fmt.Errorf("failed to dispatch request to API Gateway: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		respBody, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("API Gateway returned status %d: %s", resp.StatusCode, string(respBody))
	}

	return nil
}
