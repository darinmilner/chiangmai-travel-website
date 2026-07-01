package router

import (
	"html/template"
	"log"
	"net/http"
	"os"
	"path/filepath"

	"api/internal/handlers"

	"github.com/gin-gonic/gin"
)

func SetupRouter() *gin.Engine {
	if os.Getenv("GIN_MODE") == "release" {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.Default()

	// ---------- Load Templates Correctly ----------
	// Create a new template set
	tmpl := template.New("").Funcs(template.FuncMap{
		"add": func(a, b int) int { return a + b },
	})

	// Step 1: Parse the base layout FIRST
	basePath := filepath.Join("templates", "layouts", "base.html")
	tmpl, err := tmpl.ParseFiles(basePath)
	if err != nil {
		log.Fatalf("❌ Failed to parse base template: %v", err)
	}

	// Step 2: Parse ALL page templates and add them to the SAME template set
	pagePattern := filepath.Join("templates", "pages", "*.html")
	tmpl, err = tmpl.ParseGlob(pagePattern)
	if err != nil {
		log.Fatalf("❌ Failed to parse page templates: %v", err)
	}

	// Debug: Print all available templates
	log.Println("📋 Available templates:")
	for _, t := range tmpl.Templates() {
		log.Printf("  - %s", t.Name())
	}

	// Set the parsed templates in Gin
	r.SetHTMLTemplate(tmpl)

	// ---------- Static Files ----------
	r.Static("/static", "./static")
	r.Static("/videos", "./videos")

	// ---------- Health Check ----------
	r.GET("/health", handlers.HealthCheck)

	// ---------- Pages ----------
	r.GET("/", handlers.HomePage)

	r.GET("/villa", func(c *gin.Context) {
		c.HTML(http.StatusOK, "villa.html", gin.H{
			"Title":      "The Villa",
			"ActivePage": "villa",
		})
	})

	r.GET("/hostel", func(c *gin.Context) {
		c.HTML(http.StatusOK, "hostel.html", gin.H{
			"Title":      "The Hostel",
			"ActivePage": "hostel",
		})
	})

	r.GET("/meatshop", func(c *gin.Context) {
		c.HTML(http.StatusOK, "meatshop.html", gin.H{
			"Title":      "The Meat Shop",
			"ActivePage": "meatshop",
		})
	})

	r.GET("/blog", func(c *gin.Context) {
		c.HTML(http.StatusOK, "blog.html", gin.H{
			"Title":      "Blog",
			"ActivePage": "blog",
		})
	})

	r.GET("/contact", func(c *gin.Context) {
		c.HTML(http.StatusOK, "contact.html", gin.H{
			"Title":      "Contact Us",
			"ActivePage": "contact",
		})
	})

	return r
}
