# ============================================
# Stage 1: Download Tailwind CSS Standalone CLI
# ============================================
FROM alpine:latest AS tailwind-downloader

# Install curl and unzip
RUN apk add --no-cache curl unzip

# Create directory for Tailwind
WORKDIR /tailwind

# Download the latest Tailwind CSS standalone CLI for Linux (x86_64)
RUN curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64 \
    && chmod +x tailwindcss-linux-x64 \
    && mv tailwindcss-linux-x64 tailwindcss

# ============================================
# Stage 2: Build Tailwind CSS
# ============================================
FROM alpine:latest AS tailwind-builder

# Install ca-certificates for HTTPS
RUN apk add --no-cache ca-certificates

WORKDIR /app

# Copy Tailwind executable from downloader stage
COPY --from=tailwind-downloader /tailwind/tailwindcss /usr/local/bin/tailwindcss

# Copy Tailwind source files
COPY static/css/tailwind.css ./static/css/
COPY tailwind.config.js ./

# Build CSS (minified)
RUN tailwindcss -i ./static/css/tailwind.css -o ./static/css/styles.css --minify

# ============================================
# Stage 3: Build Go Application
# ============================================
FROM golang:1.25-alpine AS go-builder

# Install build dependencies
RUN apk add --no-cache git ca-certificates

WORKDIR /app

# Copy go.mod and go.sum first for better caching
COPY go.mod go.sum ./
RUN go mod download && go mod verify

# Copy the rest of the source code
COPY . .

# Build the Go binary with optimizations
# -ldflags: strip debug info, set build time
# CGO_ENABLED=0: static binary for Alpine compatibility
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags="-w -s -X main.buildTime=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    -o /app/main ./cmd/server

# ============================================
# Stage 4: Final Stage (Slim Production Image)
# ============================================
FROM alpine:latest

# Install ca-certificates for HTTPS outbound calls
RUN apk --no-cache add ca-certificates tzdata

# Create a non-root user for security
RUN addgroup -g 1000 -S appuser && \
    adduser -u 1000 -S appuser -G appuser

WORKDIR /app

# Copy the Go binary from builder stage
COPY --from=go-builder /app/main /app/main

# Copy templates
COPY --chown=appuser:appuser ./templates /app/templates

# Copy compiled CSS from tailwind-builder stage
COPY --from=tailwind-builder /app/static/css/styles.css /app/static/css/styles.css

# Copy static assets (images, JS files)
COPY --chown=appuser:appuser ./static /app/static
COPY --chown=appuser:appuser ./videos /app/videos

# Set ownership of the working directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Run the application
CMD ["/app/main"]