# Configuration Files

This directory contains configuration files for the Smart Video Content Moderator.

## Current Status

The system has been enhanced to use BLIP-1 natural language descriptions instead of CLIP-based label files. 

### Removed Files
- `clip_labels.txt` - No longer needed as BLIP provides natural language descriptions

### BLIP-Enhanced System
The system now uses:
- Natural language descriptions from BLIP-1 model
- Context-aware policy evaluation
- No external label files required

## Future Configuration

If needed, this directory can contain:
- Model configuration files
- Policy tuning parameters
- Threshold settings
- Custom rule definitions

## BLIP Model Configuration

The BLIP model is automatically downloaded from Hugging Face:
- Model: `Salesforce/blip-image-captioning-base`
- Processor: `Salesforce/blip-image-captioning-base`

No manual configuration required.
