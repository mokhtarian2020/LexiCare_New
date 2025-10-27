#!/usr/bin/env python3
"""
Demo showing improved comparison explanations with specific differences
"""

def show_improved_explanations():
    """Show examples of improved comparison explanations"""
    
    print("🔍 LexiCare - Improved Comparison Explanations")
    print("=" * 60)
    
    print("""
💡 YOU REQUESTED: "Say shortly, in a short paragraph say what differences 
you saw that you did inference like that"

✅ IMPLEMENTED: Updated AI prompt to include specific differences!
""")

    # Example scenarios with specific differences
    examples = [
        {
            "status": "🔴 PEGGIORATA",
            "old_explanation": "La situazione clinica è peggiorata.",
            "new_explanation": "Le proteine nelle urine sono aumentate da 15 mg/dl a 45 mg/dl (normale: 0-10), sono comparsi leucociti elevati (75 Leu/ul vs precedenti 5 Leu/ul) e tracce di sangue (0.50 mg/dl vs precedente assente). Il peso specifico è aumentato da 1.015 a 1.020, indicando possibile infezione del tratto urinario."
        },
        {
            "status": "🟢 MIGLIORATA", 
            "old_explanation": "La situazione clinica è migliorata.",
            "new_explanation": "Le proteine sono diminuite significativamente da 45 mg/dl a 15 mg/dl, i leucociti sono rientrati nella norma (da 75 a 5 Leu/ul) e non si rileva più sangue nelle urine. L'aspetto è tornato limpido vs il precedente velato, indicando risoluzione dell'infezione."
        },
        {
            "status": "⚪ INVARIATA",
            "old_explanation": "La situazione clinica è invariata.",
            "new_explanation": "I valori rimangono stabili: proteine 30 mg/dl (vs 30 mg/dl precedente), leucociti 10 Leu/ul (vs 8 Leu/ul), pH 6.0 (vs 6.1). Non si evidenziano cambiamenti clinicamente significativi tra i due referti."
        }
    ]
    
    print("\n📊 BEFORE vs AFTER Examples:")
    print("-" * 50)
    
    for example in examples:
        print(f"\n{example['status']}")
        print("─" * 30)
        print("❌ OLD (Generic):")
        print(f"   {example['old_explanation']}")
        print("\n✅ NEW (Specific Differences):")
        print(f"   {example['new_explanation']}")
        print()
    
    print("🎯 KEY IMPROVEMENTS:")
    print("-" * 20)
    print("✅ Specific numerical values (15 mg/dl → 45 mg/dl)")
    print("✅ Reference ranges mentioned (normale: 0-10)")
    print("✅ Multiple parameters compared")
    print("✅ Clinical interpretation of changes")
    print("✅ Clear explanation of WHY status was assigned")

if __name__ == "__main__":
    show_improved_explanations()
