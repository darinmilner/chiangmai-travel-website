package secrets

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/secretsmanager"
)

// ContactConfig holds the configuration for the contact form
type ContactConfig struct {
	RecipientEmail string `json:"recipient_email"`
	SenderEmail    string `json:"sender_email"`
	APIURL         string `json:"api_url"`
}

// AppConfig holds all application configuration from secrets
type AppConfig struct {
	Contact ContactConfig `json:"contact"`
}

// SecretManager handles AWS Secrets Manager operations
type SecretManager struct {
	client *secretsmanager.Client
	ctx    context.Context
}

// NewSecretManager creates a new SecretManager instance
func NewSecretManager() (*SecretManager, error) {
	ctx := context.Background()

	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to load AWS config: %w", err)
	}

	client := secretsmanager.NewFromConfig(cfg)

	return &SecretManager{
		client: client,
		ctx:    ctx,
	}, nil
}

// GetSecret retrieves a secret value from AWS Secrets Manager
func (sm *SecretManager) GetSecret(secretName string) (string, error) {
	input := &secretsmanager.GetSecretValueInput{
		SecretId: aws.String(secretName),
	}

	result, err := sm.client.GetSecretValue(sm.ctx, input)
	if err != nil {
		return "", fmt.Errorf("failed to get secret %s: %w", secretName, err)
	}

	if result.SecretString == nil {
		return "", fmt.Errorf("secret %s has no string value", secretName)
	}

	return *result.SecretString, nil
}

// GetSecretJSON retrieves and unmarshals a secret value
func (sm *SecretManager) GetSecretJSON(secretName string, target interface{}) error {
	secretString, err := sm.GetSecret(secretName)
	if err != nil {
		return err
	}

	return json.Unmarshal([]byte(secretString), target)
}

// GetContactConfig retrieves contact configuration from secrets
func (sm *SecretManager) GetContactConfig() (*ContactConfig, error) {
	var config ContactConfig

	// Try to get from secrets first
	err := sm.GetSecretJSON("contact/config", &config)
	if err == nil {
		return &config, nil
	}

	// Fallback to environment variables
	config.RecipientEmail = os.Getenv("RECIPIENT_EMAIL")
	config.SenderEmail = os.Getenv("SENDER_EMAIL")
	config.APIURL = os.Getenv("CONTACT_API_URL")

	if config.RecipientEmail == "" {
		config.RecipientEmail = "admin@yourvilla.com"
	}
	if config.SenderEmail == "" {
		config.SenderEmail = "noreply@yourvilla.com"
	}
	if config.APIURL == "" {
		config.APIURL = "https://your-api-gateway-url.com/contact"
	}

	return &config, nil
}

// LoadConfigFromEnv loads configuration from environment variables (for local development)
func LoadConfigFromEnv() (*AppConfig, error) {
	config := &AppConfig{
		Contact: ContactConfig{
			RecipientEmail: os.Getenv("RECIPIENT_EMAIL"),
			SenderEmail:    os.Getenv("SENDER_EMAIL"),
			APIURL:         os.Getenv("CONTACT_API_URL"),
		},
	}

	if config.Contact.RecipientEmail == "" {
		config.Contact.RecipientEmail = "admin@yourvilla.com"
	}
	if config.Contact.SenderEmail == "" {
		config.Contact.SenderEmail = "noreply@yourvilla.com"
	}
	if config.Contact.APIURL == "" {
		config.Contact.APIURL = "https://your-api-gateway-url.com/contact"
	}

	log.Printf("📧 Contact config loaded:")
	log.Printf("   Recipient: %s", config.Contact.RecipientEmail)
	log.Printf("   Sender: %s", config.Contact.SenderEmail)
	log.Printf("   API URL: %s", config.Contact.APIURL)

	return config, nil
}

// GetEnv gets an environment variable with a default fallback
func GetEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
