    
    def _enhance_captions_with_vision(self, figures: List[Figure]) -> int:
        """
        Use NVIDIA Llama 3.2 Vision to enhance figure captions.
        
        Args:
            figures: List of figures to analyze
        
        Returns:
            Number of figures enhanced
        """
        enhanced_count = 0
        
        for figure in figures:
            # Skip if no image path
            if not figure.export_path or not os.path.exists(figure.export_path):
                continue
            
            try:
                # Analyze figure with vision model
                vision_description = self.vision_client.analyze_figure(
                    image_path=figure.export_path,
                    caption=figure.caption_text
                )
                
                if vision_description:
                    # Store vision analysis in metadata
                    figure.metadata["vision_analysis"] = vision_description
                    
                    # If no caption exists, use vision analysis as caption
                    if not figure.caption_text or figure.caption_text.strip() == "":
                        figure.caption_text = f"Figure {figure.figure_id}: {vision_description}"
                        figure.metadata["caption_source"] = "vision_generated"
                        print(f"✅ Generated caption for Figure {figure.figure_id} using vision")
                    else:
                        # Caption exists, just store analysis for reference
                        figure.metadata["caption_source"] = "manual_with_vision"
                        print(f"✅ Enhanced Figure {figure.figure_id} with vision analysis")
                    
                    enhanced_count += 1
            
            except Exception as e:
                print(f"⚠️ Vision analysis failed for Figure {figure.figure_id}: {e}")
                continue
        
        return enhanced_count

# Convenience function
def link_figures(document: Document, enable_vision: bool = True) -> Document:
    matcher = CaptionMatcher(enable_vision=enable_vision)
    return matcher.process(document)
