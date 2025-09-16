import unittest
from unittest.mock import MagicMock, patch
from backend.core.pdf_parser import normalize_report_type, extract_exam_title


class TestPdfParser(unittest.TestCase):

    def test_normalize_report_type(self):
        # Test direct matches
        self.assertEqual(normalize_report_type("radiologia"), "radiologia")
        self.assertEqual(normalize_report_type("laboratorio"), "laboratorio")
        self.assertEqual(normalize_report_type("patologia"), "patologia")
        
        # Test case insensitivity
        self.assertEqual(normalize_report_type("RADIOLOGIA"), "radiologia")
        self.assertEqual(normalize_report_type("Laboratorio"), "laboratorio")
        self.assertEqual(normalize_report_type("PaToLoGiA"), "patologia")
        
        # Test whitespace handling
        self.assertEqual(normalize_report_type("  radiologia  "), "radiologia")
        
        # Test problematic values from real-world issues
        self.assertEqual(normalize_report_type("sconosciuto"), "radiologia")
        self.assertEqual(normalize_report_type("ID PAZIENTE:"), "radiologia")
        self.assertEqual(normalize_report_type("unknown"), "radiologia")
        self.assertEqual(normalize_report_type(None), "radiologia")
        self.assertEqual(normalize_report_type(""), "radiologia")
        
        # Test variants mapping
        self.assertEqual(normalize_report_type("REFERTO RADIOLOGICO"), "radiologia")
        self.assertEqual(normalize_report_type("TAC ADDOME"), "radiologia")
        self.assertEqual(normalize_report_type("ECOGRAFIA RENALE"), "radiologia")
        self.assertEqual(normalize_report_type("RISONANZA MAGNETICA"), "radiologia")
        
        self.assertEqual(normalize_report_type("ESAMI DEL SANGUE"), "laboratorio")
        self.assertEqual(normalize_report_type("EMOCROMO COMPLETO"), "laboratorio")
        self.assertEqual(normalize_report_type("ANALISI CLINICHE"), "laboratorio")
        self.assertEqual(normalize_report_type("TEST MICROBIOLOGICO"), "laboratorio")
        
        self.assertEqual(normalize_report_type("ESAME ISTOLOGICO"), "patologia")
        self.assertEqual(normalize_report_type("BIOPSIA MAMMARIA"), "patologia")
        self.assertEqual(normalize_report_type("REFERTO CITOLOGICO"), "patologia")
        self.assertEqual(normalize_report_type("ANATOMIA PATOLOGICA"), "patologia")
        
        # Test fallback for unknown types
        self.assertEqual(normalize_report_type("DOCUMENTO GENERICO"), "radiologia")
        self.assertEqual(normalize_report_type("FOGLIO INFORMATIVO"), "radiologia")


if __name__ == "__main__":
    unittest.main()
