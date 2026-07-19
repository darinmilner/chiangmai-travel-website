package secrets

import (
	"encoding/json"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestLoadConfigFromEnv(t *testing.T) {
	t.Run("should load config from environment variables", func(t *testing.T) {
		// Set environment variables
		os.Setenv("RECIPIENT_EMAIL", "test@example.com")
		os.Setenv("SENDER_EMAIL", "noreply@test.com")
		os.Setenv("CONTACT_API_URL", "https://test-api.com/contact")

		defer func() {
			os.Unsetenv("RECIPIENT_EMAIL")
			os.Unsetenv("SENDER_EMAIL")
			os.Unsetenv("CONTACT_API_URL")
		}()

		config, err := LoadConfigFromEnv()
		assert.NoError(t, err)
		assert.NotNil(t, config)
		assert.Equal(t, "test@example.com", config.Contact.RecipientEmail)
		assert.Equal(t, "noreply@test.com", config.Contact.SenderEmail)
		assert.Equal(t, "https://test-api.com/contact", config.Contact.APIURL)
	})

	t.Run("should use defaults when environment variables are not set", func(t *testing.T) {
		// Clear environment variables
		os.Unsetenv("RECIPIENT_EMAIL")
		os.Unsetenv("SENDER_EMAIL")
		os.Unsetenv("CONTACT_API_URL")

		config, err := LoadConfigFromEnv()
		assert.NoError(t, err)
		assert.NotNil(t, config)
		assert.Equal(t, "admin@yourvilla.com", config.Contact.RecipientEmail)
		assert.Equal(t, "noreply@yourvilla.com", config.Contact.SenderEmail)
		assert.Equal(t, "https://your-api-gateway-url.com/contact", config.Contact.APIURL)
	})
}

func TestGetEnv(t *testing.T) {
	t.Run("should return environment variable when set", func(t *testing.T) {
		os.Setenv("TEST_VAR", "test-value")
		defer os.Unsetenv("TEST_VAR")

		result := GetEnv("TEST_VAR", "default")
		assert.Equal(t, "test-value", result)
	})

	t.Run("should return default when environment variable is not set", func(t *testing.T) {
		os.Unsetenv("TEST_VAR")

		result := GetEnv("TEST_VAR", "default")
		assert.Equal(t, "default", result)
	})
}

func TestContactConfig(t *testing.T) {
	t.Run("should create valid contact config", func(t *testing.T) {
		config := &ContactConfig{
			RecipientEmail: "admin@yourvilla.com",
			SenderEmail:    "noreply@yourvilla.com",
			APIURL:         "https://api.example.com/contact",
		}

		// Test JSON serialization
		jsonBytes, err := json.Marshal(config)
		assert.NoError(t, err)

		var parsed ContactConfig
		err = json.Unmarshal(jsonBytes, &parsed)
		assert.NoError(t, err)
		assert.Equal(t, config.RecipientEmail, parsed.RecipientEmail)
		assert.Equal(t, config.SenderEmail, parsed.SenderEmail)
		assert.Equal(t, config.APIURL, parsed.APIURL)
	})
}
