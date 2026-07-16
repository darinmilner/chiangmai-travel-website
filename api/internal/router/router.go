package router

import (
	"html/template"
	"net/http"
	"os"
	"path/filepath"

	"api/internal/handlers"

	"github.com/gin-contrib/multitemplate"
	"github.com/gin-gonic/gin"
)

func SetupRouter() *gin.Engine {
	if os.Getenv("GIN_MODE") == "release" {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.Default()

	funcMap := template.FuncMap{
		"add": func(a, b int) int {
			return a + b
		},
		"iterate": func(count int) []int {
			result := make([]int, count)
			for i := 0; i < count; i++ {
				result[i] = i
			}
			return result
		},
		"safe": func(s string) template.HTML {
			return template.HTML(s)
		},
	}

	r.HTMLRender = createRenderer(funcMap)

	r.Static("/static", "./static")
	r.Static("/videos", "./videos")

	r.GET("/health", handlers.HealthCheck)

	r.GET("/", func(c *gin.Context) {
		data := handlers.GetHomepageData()
		if data == nil {
			c.String(http.StatusInternalServerError, "Data not loaded")
			return
		}

		// If your homepage data doesn't already include this,
		// uncomment the next line after adding ActivePage.
		// data.ActivePage = "home"

		c.HTML(http.StatusOK, "index.html", data)
	})

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

	// Contact form API
	r.POST("/api/contact", handlers.ContactForm)

	return r
}

func createRenderer(funcMap template.FuncMap) multitemplate.Renderer {
	renderer := multitemplate.New()

	layout := "templates/layouts/base.html"

	partials, err := filepath.Glob("templates/partials/*.html")
	if err != nil {
		panic(err)
	}

	pages, err := filepath.Glob("templates/pages/*.html")
	if err != nil {
		panic(err)
	}

	for _, page := range pages {

		files := []string{
			layout,
		}

		files = append(files, partials...)
		files = append(files, page)

		renderer.AddFromFilesFuncs(
			filepath.Base(page),
			funcMap,
			files...,
		)
	}

	return renderer
}
