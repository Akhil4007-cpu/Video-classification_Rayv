#!/usr/bin/env python3
"""
Isolated test for fire safety policy
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from policies.fire_safety import evaluate_fire_safety

# Test signals
test_signals = {
    'entity': {'fire_present': True, 'risky_objects': ['fire', 'burning']},
    'scene_labels': [('risky_scene: a building on fire with people running', 0.8)],
    'visual_state': {'fire_visible': True},
    'motion': {'motion_score': 70.0, 'aggressive_motion': True, 'sudden_motion': True},
    'audio': {'audio_risk': 0.9, 'panic_audio': True},
    'temporal': {'sustained': False, 'impact_detected': False, 'possible_accident': False}
}

print('🔥 Isolated Fire Safety Test')
print('=' * 50)

risk, reasons = evaluate_fire_safety(test_signals)
print(f'Risk: {risk}')
print(f'Reasons: {reasons}')

if risk > 0.5:
    print('✅ CORRECT: Fire detected as UNSAFE')
else:
    print('❌ ISSUE: Fire should be detected as UNSAFE')
