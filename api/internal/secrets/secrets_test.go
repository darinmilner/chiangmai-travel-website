package secrets

import (
	"encoding/json"
	"errors"
	"testing"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/secretsmanager"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

// ============================================
// Mock AWS Secrets Manager Client
// ============================================

// MockSecretsManagerClient is a mock implementation of the SecretsManager client
type MockSecretsManagerClient struct {
	mock.Mock
}

// GetSecretValue mocks the GetSecretValue method
func (m *MockSecretsManagerClient) GetSecretValue(input *secretsmanager.GetSecretValueInput) (*secretsmanager.GetSecretValueOutput, error) {
	args := m.Called(input)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*secretsmanager.GetSecretValueOutput), args.Error(1)
}

// ============================================
// Helper Functions
// ============================================

// createMockSecretManager creates a SecretManager with a mock client
func createMockSecretManager(client *MockSecretsManagerClient) *SecretManager {
	return &SecretManager{
		client: client,
	}
}

// createMockSecretString creates a mock secret string value
func createMockSecretString(value interface{}) string {
	jsonBytes, _ := json.Marshal(value)
	return string(jsonBytes)
}

// ============================================
// Tests
// ============================================

func TestNewSecretManager(t *testing.T) {
	t.Run("should create a new SecretManager without error", func(t *testing.T) {
		sm, err := NewSecretManager()
		// Note: This test will fail if AWS credentials are not configured
		// In a real CI environment, you might want to skip this test
		if err != nil {
			t.Skip("Skipping test: AWS credentials not configured")
		}
		assert.NotNil(t, sm)
		assert.NotNil(t, sm.client)
	})
}

func TestSecretManager_GetSecret(t *testing.T) {
	t.Run("should return secret value when successful", func(t *testing.T) {
		// Arrange
		mockClient := new(MockSecretsManagerClient)
		sm := createMockSecretManager(mockClient)

		secretName := "test/secret"
		expectedValue := "secret-value-123"

		mockClient.On("GetSecretValue", &secretsmanager.GetSecretValueInput{
			SecretId: aws.String(secretName),
		}).Return(&secretsmanager.GetSecretValueOutput{
			SecretString: aws.String(expectedValue),
		}, nil)

		// Act
		result, err := sm.GetSecret(secretName)

		// Assert
		assert.NoError(t, err)
		assert.Equal(t, expectedValue, result)
		mockClient.AssertExpectations(t)
	})

	t.Run("should return error when AWS returns error", func(t *testing.T) {
		// Arrange
		mockClient := new(MockSecretsManagerClient)
		sm := createMockSecretManager(mockClient)

		secretName := "test/secret"
		expectedError := errors.New("secret not found")

		mockClient.On("GetSecretValue", &secretsmanager.GetSecretValueInput{
			SecretId: aws.String(secretName),
		}).Return(nil, expectedError)

		// Act
		result, err := sm.GetSecret(secretName)

		// Assert
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "failed to get secret")
		assert.Empty(t, result)
		mockClient.AssertExpectations(t)
	})

	t.Run("should return error when SecretString is nil", func(t *testing.T) {
		// Arrange
		mockClient := new(MockSecretsManagerClient)
		sm := createMockSecretManager(mockClient)

		secretName := "test/secret"

		mockClient.On("GetSecretValue", &secretsmanager.GetSecretValueInput{
			SecretId: aws.String(secretName),
		}).Return(&secretsmanager.GetSecretValueOutput{
			SecretString: nil,
		}, nil)

		// Act
		result, err := sm.GetSecret(secretName)

		// Assert
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "has no string value")
		assert.Empty(t, result)
		mockClient.AssertExpectations(t)
	})
}

func TestSecretManager_GetSecretJSON(t *testing.T) {
	t.Run("should unmarshal JSON secret successfully", func(t *testing.T) {
		// Arrange
		mockClient := new(MockSecretsManagerClient)
		sm := createMockSecretManager(mockClient)

		secretName := "test/config"
		expectedConfig := map[string]interface{}{
			"host":     "localhost",
			"port":     5432,
			"username": "admin",
			"password": "password123",
		}
		mockSecret := createMockSecretString(expectedConfig)

		mockClient.On("GetSecretValue", &secretsmanager.GetSecretValueInput{
			SecretId: aws.String(secretName),
		}).Return(&secretsmanager.GetSecretValueOutput{
			SecretString: aws.String(mockSecret),
		}, nil)

		// Act
		var result map[string]interface{}
		err := sm.GetSecretJSON(secretName, &result)

		// Assert
		assert.NoError(t, err)
		assert.Equal(t, expectedConfig["host"], result["host"])
		assert.Equal(t, expectedConfig["port"], result["port"])
		assert.Equal(t, expectedConfig["username"], result["username"])
		assert.Equal(t, expectedConfig["password"], result["password"])
		mockClient.AssertExpectations(t)
	})

	t.Run("should return error when secret is invalid JSON", func(t *testing.T) {
		// Arrange
		mockClient := new(MockSecretsManagerClient)
		sm := createMockSecretManager(mockClient)

		secretName := "test/invalid"
		invalidJSON := "{invalid json}"

		mockClient.On("GetSecretValue", &secretsmanager.GetSecretValueInput{
			SecretId: aws.String(secretName),
		}).Return(&secretsmanager.GetSecretValueOutput{
			SecretString: aws.String(invalidJSON),
		}, nil)

		// Act
		var result map[string]interface{}
		err := sm.GetSecretJSON(secretName, &result)

		// Assert
		assert.Error(t, err)
		mockClient.AssertExpectations(t)
	})

	t.Run("should return error when GetSecret fails", func(t *testing.T) {
		// Arrange
		mockClient := new(MockSecretsManagerClient)
		sm := createMockSecretManager(mockClient)

		secretName := "test/fail"
		expectedError := errors.New("AWS error")

		mockClient.On("GetSecretValue", &secretsmanager.GetSecretValueInput{
			SecretId: aws.String(secretName),
		}).Return(nil, expectedError)

		// Act
		var result map[string]interface{}
		err := sm.GetSecretJSON(secretName, &result)

		// Assert
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "failed to get secret")
		mockClient.AssertExpectations(t)
	})
}

func TestSecretManager_GetDatabaseConfig(t *testing.T) {
	t.Run("should return database config successfully", func(t *testing.T) {
		// Arrange
		mockClient := new(MockSecretsManagerClient)
		sm := createMockSecretManager(mockClient)

		expectedConfig := DatabaseConfig{
			Username: "app_user",
			Password: "secure_password",
			Host:     "prod-db.example.com",
			Port:     "5432",
			Database: "travel_db",
		}
		mockSecret := createMockSecretString(expectedConfig)

		mockClient.On("GetSecretValue", &secretsmanager.GetSecretValueInput{
			SecretId: aws.String("db/credentials"),
		}).Return(&secretsmanager.GetSecretValueOutput{
			SecretString: aws.String(mockSecret),
		}, nil)

		// Act
		config, err := sm.GetDatabaseConfig()

		// Assert
		assert.NoError(t, err)
		assert.NotNil(t, config)
		assert.Equal(t, expectedConfig.Username, config.Username)
		assert.Equal(t, expectedConfig.Password, config.Password)
		assert.Equal(t, expectedConfig.Host, config.Host)
		assert.Equal(t, expectedConfig.Port, config.Port)
		assert.Equal(t, expectedConfig.Database, config.Database)
		mockClient.AssertExpectations(t)
	})

	t.Run("should return error when GetSecretJSON fails", func(t *testing.T) {
		// Arrange
		mockClient := new(MockSecretsManagerClient)
		sm := createMockSecretManager(mockClient)

		mockClient.On("GetSecretValue", &secretsmanager.GetSecretValueInput{
			SecretId: aws.String("db/credentials"),
		}).Return(nil, errors.New("secret not found"))

		// Act
		config, err := sm.GetDatabaseConfig()

		// Assert
		assert.Error(t, err)
		assert.Nil(t, config)
		mockClient.AssertExpectations(t)
	})
}

func TestSecretManager_GetConnectionString(t *testing.T) {
	t.Run("should return connection string successfully", func(t *testing.T) {
		// Arrange
		mockClient := new(MockSecretsManagerClient)
		sm := createMockSecretManager(mockClient)

		config := DatabaseConfig{
			Username: "app_user",
			Password: "secure_password",
			Host:     "prod-db.example.com",
			Port:     "5432",
			Database: "travel_db",
		}
		mockSecret := createMockSecretString(config)

		mockClient.On("GetSecretValue", &secretsmanager.GetSecretValueInput{
			SecretId: aws.String("db/credentials"),
		}).Return(&secretsmanager.GetSecretValueOutput{
			SecretString: aws.String(mockSecret),
		}, nil)

		// Act
		connStr, err := sm.GetConnectionString()

		// Assert
		assert.NoError(t, err)
		expected := "host=prod-db.example.com port=5432 user=app_user password=secure_password dbname=travel_db sslmode=require"
		assert.Equal(t, expected, connStr)
		mockClient.AssertExpectations(t)
	})

	t.Run("should return error when GetDatabaseConfig fails", func(t *testing.T) {
		// Arrange
		mockClient := new(MockSecretsManagerClient)
		sm := createMockSecretManager(mockClient)

		mockClient.On("GetSecretValue", &secretsmanager.GetSecretValueInput{
			SecretId: aws.String("db/credentials"),
		}).Return(nil, errors.New("AWS error"))

		// Act
		connStr, err := sm.GetConnectionString()

		// Assert
		assert.Error(t, err)
		assert.Empty(t, connStr)
		mockClient.AssertExpectations(t)
	})
}

func TestLoadSecretsFromEnv(t *testing.T) {
	t.Run("should not return error when all secrets are set", func(t *testing.T) {
		// This is a no-op test - the function only logs warnings
		err := LoadSecretsFromEnv()
		assert.NoError(t, err)
	})
}

// ============================================
// Table-Driven Tests
// ============================================

func TestSecretManager_GetSecret_TableDriven(t *testing.T) {
	tests := []struct {
		name          string
		secretName    string
		mockResponse  *secretsmanager.GetSecretValueOutput
		mockError     error
		expectedValue string
		expectError   bool
	}{
		{
			name:       "successful retrieval",
			secretName: "test/success",
			mockResponse: &secretsmanager.GetSecretValueOutput{
				SecretString: aws.String("success-value"),
			},
			mockError:     nil,
			expectedValue: "success-value",
			expectError:   false,
		},
		{
			name:       "AWS error",
			secretName: "test/error",
			mockResponse: &secretsmanager.GetSecretValueOutput{
				SecretString: nil,
			},
			mockError:     errors.New("AWS service error"),
			expectedValue: "",
			expectError:   true,
		},
		{
			name:       "nil secret string",
			secretName: "test/nil",
			mockResponse: &secretsmanager.GetSecretValueOutput{
				SecretString: nil,
			},
			mockError:     nil,
			expectedValue: "",
			expectError:   true,
		},
		{
			name:       "empty secret string",
			secretName: "test/empty",
			mockResponse: &secretsmanager.GetSecretValueOutput{
				SecretString: aws.String(""),
			},
			mockError:     nil,
			expectedValue: "",
			expectError:   false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Arrange
			mockClient := new(MockSecretsManagerClient)
			sm := createMockSecretManager(mockClient)

			mockClient.On("GetSecretValue", &secretsmanager.GetSecretValueInput{
				SecretId: aws.String(tt.secretName),
			}).Return(tt.mockResponse, tt.mockError)

			// Act
			result, err := sm.GetSecret(tt.secretName)

			// Assert
			if tt.expectError {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.expectedValue, result)
			}
			mockClient.AssertExpectations(t)
		})
	}
}

// ============================================
// Benchmark Tests
// ============================================

func BenchmarkSecretManager_GetSecret(b *testing.B) {
	// Arrange
	mockClient := new(MockSecretsManagerClient)
	sm := createMockSecretManager(mockClient)

	secretName := "test/benchmark"
	expectedValue := "benchmark-value"

	mockClient.On("GetSecretValue", &secretsmanager.GetSecretValueInput{
		SecretId: aws.String(secretName),
	}).Return(&secretsmanager.GetSecretValueOutput{
		SecretString: aws.String(expectedValue),
	}, nil)

	// Reset benchmark timer
	b.ResetTimer()

	// Run benchmark
	for i := 0; i < b.N; i++ {
		_, _ = sm.GetSecret(secretName)
	}
}

func BenchmarkSecretManager_GetSecretJSON(b *testing.B) {
	// Arrange
	mockClient := new(MockSecretsManagerClient)
	sm := createMockSecretManager(mockClient)

	secretName := "test/benchmark"
	config := map[string]interface{}{
		"host": "localhost",
		"port": 5432,
	}
	mockSecret := createMockSecretString(config)

	mockClient.On("GetSecretValue", &secretsmanager.GetSecretValueInput{
		SecretId: aws.String(secretName),
	}).Return(&secretsmanager.GetSecretValueOutput{
		SecretString: aws.String(mockSecret),
	}, nil)

	// Reset benchmark timer
	b.ResetTimer()

	// Run benchmark
	for i := 0; i < b.N; i++ {
		var result map[string]interface{}
		_ = sm.GetSecretJSON(secretName, &result)
	}
}
