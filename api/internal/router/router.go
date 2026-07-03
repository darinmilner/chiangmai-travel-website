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

	// ---------- Load Templates ----------
	tmpl := template.New("").Funcs(template.FuncMap{
		"add": func(a, b int) int { return a + b },
		"iterate": func(count int) []int {
			var result []int
			for i := 0; i < count; i++ {
				result = append(result, i)
			}
			return result
		},
		"safe": func(s string) template.HTML {
			return template.HTML(s)
		},
	})

	// Parse base layout
	basePath := filepath.Join("templates", "layouts", "base.html")
	tmpl, err := tmpl.ParseFiles(basePath)
	if err != nil {
		log.Fatalf("❌ Failed to parse base template: %v", err)
	}

	// Parse all page templates
	pagePattern := filepath.Join("templates", "pages", "*.html")
	tmpl, err = tmpl.ParseGlob(pagePattern)
	if err != nil {
		log.Fatalf("❌ Failed to parse page templates: %v", err)
	}

	log.Println("📋 Available templates:")
	for _, t := range tmpl.Templates() {
		log.Printf("  - %s", t.Name())
	}

	r.SetHTMLTemplate(tmpl)

	// ---------- Static Files ----------
	r.Static("/static", "./static")
	r.Static("/videos", "./videos")

	// ---------- Routes ----------
	r.GET("/health", handlers.HealthCheck)
	r.GET("/", handlers.HomePage)
	
	// Debug route
	r.GET("/debug/data", func(c *gin.Context) {
		data := handlers.GetHomepageData()
		if data == nil {
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": "Homepage data is nil",
			})
			return
		}
		c.JSON(http.StatusOK, gin.H{
			"features":     len(data.Features),
			"reasons":      len(data.Reasons),
			"testimonials": len(data.Testimonials),
			"sample_feature": data.Features,
		})
	})

	// Placeholder routes
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