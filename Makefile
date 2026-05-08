RESUME_SRC := Resume.typ
RESUME_PDF := Resume.pdf
RESUME_PREVIEW := /tmp/rishabh-resume-preview.png

.PHONY: resume check-resume preview-resume

resume:
	typst compile $(RESUME_SRC) $(RESUME_PDF)

check-resume: resume
	pdfinfo $(RESUME_PDF) | grep 'Pages:           1'

preview-resume: check-resume
	pdftoppm -png -singlefile -r 160 $(RESUME_PDF) /tmp/rishabh-resume-preview
	@echo $(RESUME_PREVIEW)
