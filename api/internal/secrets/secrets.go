package secrets

import (
	"encoding/json"
	"fmt"
	"log"
	"os"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/secretsmanager"
)

// SecretManager handles AWS Secrets Manager operations
type SecretManager struct {
	client *secretsmanager.SecretsManager
}

// NewSecretManager creates a new SecretManager instance
func NewSecretManager() (*SecretManager, error) {
	sess, err := session.NewSession()
	if err != nil {
		return nil, fmt.Errorf("failed to create AWS session: %w", err)
	}

	client := secretsmanager.New(sess)
	return &SecretManager{client: client}, nil
}

// GetSecret retrieves a secret value from AWS Secrets Manager
func (sm *SecretManager) GetSecret(secretName string) (string, error) {
	input := &secretsmanager.GetSecretValueInput{
		SecretId: aws.String(secretName),
	}

	result, err := sm.client.GetSecretValue(input)
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

// DatabaseConfig represents database configuration from secrets
type DatabaseConfig struct {
	Username string `json:"username"`
	Password string `json:"password"`
	Host     string `json:"host"`
	Port     string `json:"port"`
	Database string `json:"database"`
}

// GetDatabaseConfig retrieves database configuration from secrets
func (sm *SecretManager) GetDatabaseConfig() (*DatabaseConfig, error) {
	var config DatabaseConfig
	err := sm.GetSecretJSON("db/credentials", &config)
	if err != nil {
		return nil, err
	}
	return &config, nil
}

// GetConnectionString returns a PostgreSQL connection string
func (sm *SecretManager) GetConnectionString() (string, error) {
	config, err := sm.GetDatabaseConfig()
	if err != nil {
		return "", err
	}

	return fmt.Sprintf(
		"host=%s port=%s user=%s password=%s dbname=%s sslmode=require",
		config.Host, config.Port, config.Username, config.Password, config.Database,
	), nil
}

// LoadSecretsFromEnv loads secrets from environment (for local development)
func LoadSecretsFromEnv() error {
	// This is a fallback for local development
	// In production, use AWS Secrets Manager
	requiredSecrets := []string{
		"DB_USERNAME",
		"DB_PASSWORD",
		"DB_HOST",
		"DB_NAME",
		"JWT_SECRET_KEY",
	}

	for _, secret := range requiredSecrets {
		if os.Getenv(secret) == "" {
			log.Printf("⚠️ Warning: %s environment variable is not set", secret)
		}
	}

	return nil
}
