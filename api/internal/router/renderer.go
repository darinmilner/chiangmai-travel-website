package router

import (
	"html/template"

	"github.com/gin-contrib/multitemplate"
)

func createRenderer(funcMap template.FuncMap) multitemplate.Renderer {
	r := multitemplate.NewRenderer()

	layout := "templates/layouts/base.html"

	partials := []string{
		"templates/partials/header.html",
		"templates/partials/footer.html",
	}

	pages := map[string]string{
		"index":    "templates/pages/index.html",
		"villa":    "templates/pages/villa.html",
		"hostel":   "templates/pages/hostel.html",
		"meatshop": "templates/pages/meatshop.html",
		"blog":     "templates/pages/blog.html",
		"contact":  "templates/pages/contact.html",
	}

	for name, page := range pages {

		files := []string{layout}
		files = append(files, partials...)
		files = append(files, page)

		tmpl := template.Must(
			template.New("base").
				Funcs(funcMap).
				ParseFiles(files...),
		)

		r.Add(name, tmpl)
	}

	return r
}
