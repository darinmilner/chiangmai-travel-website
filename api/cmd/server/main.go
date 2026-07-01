package main

import (
    "context"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "api/internal/router"
)

func main() {
    // Setup router
    r := router.SetupRouter()

    // Get port from environment
    port := os.Getenv("PORT")
    if port == "" {
        port = "8080"
    }

    // Create HTTP server
    srv := &http.Server{
        Addr:           ":" + port,
        Handler:        r,
        ReadTimeout:    15 * time.Second,
        WriteTimeout:   15 * time.Second,
        IdleTimeout:    60 * time.Second,
        MaxHeaderBytes: 1 << 20,
    }

    // Start server in a goroutine
    go func() {
        log.Printf("🚀 Server starting on http://localhost:%s", port)
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("❌ Failed to start server: %v", err)
        }
    }()

    // Wait for interrupt signal
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    log.Println("🛑 Shutting down server gracefully...")

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        log.Fatalf("❌ Server forced to shutdown: %v", err)
    }

    log.Println("✅ Server exited gracefully")
}