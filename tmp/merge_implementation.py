    async def merge_pdfs(self, pdf_paths: List[str], job_id: str = None) -> str:
        """Merge multiple PDFs into a single file preserving original names"""
        if not pdf_paths:
            raise ConversionError("No PDF files provided")
            
        if fitz is None:
            raise ConversionError("PyMuPDF not available. Please install pymupdf package.")
            
        if job_id is None:
            job_id = str(uuid.uuid4())
            
        work_dir = self._get_work_dir(job_id)
        
        try:
            def _merge_pdfs():
                # Create output filename from first PDF
                first_pdf_name = Path(pdf_paths[0]).stem if pdf_paths else "merged"
                output_filename = f"{first_pdf_name}_merge.pdf"
                output_path = work_dir / output_filename
                
                # Create merged document
                merged_doc = fitz.open()
                
                for pdf_path in pdf_paths:
                    try:
                        source_doc = fitz.open(pdf_path)
                        merged_doc.insert_pdf(source_doc)
                        source_doc.close()
                    except Exception as e:
                        logger.warning(f"Error merging {pdf_path}: {e}")
                        continue
                
                # Save merged PDF
                merged_doc.save(str(output_path))
                merged_doc.close()
                
                return str(output_path)
            
            loop = asyncio.get_event_loop()
            result_path = await loop.run_in_executor(self.executor, _merge_pdfs)
            return result_path
            
        except Exception as e:
            self._cleanup_work_dir(work_dir)
            raise ConversionError(f"PDF merge failed: {str(e)}")