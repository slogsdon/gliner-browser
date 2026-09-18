import unittest

from gliner_browser.resolver import GlinerResolver, element_for_span


class ElementForSpanTest(unittest.TestCase):
    def test_maps_extracted_span_to_its_element(self) -> None:
        rendered = '@e1 button "Cancel"\n@e2 button "Save changes"\n'
        start = rendered.index("Save changes")

        match = element_for_span(
            rendered,
            [
                {"id": "e1", "role": "button", "name": "Cancel"},
                {"id": "e2", "role": "button", "name": "Save changes"},
            ],
            {"start": start, "end": start + len("Save changes"), "confidence": 0.91},
        )

        self.assertEqual(match["id"], "e2")
        self.assertEqual(match["confidence"], 0.91)

    def test_exact_name_outranks_a_higher_confidence_semantic_false_positive(self) -> None:
        elements = [
            {"id": "e1", "role": "button", "name": "Cancel"},
            {"id": "e2", "role": "button", "name": "Save changes"},
        ]

        class FakeModel:
            def extract_entities(
                self, model_text: str, labels: list[str], **_kwargs: object
            ) -> dict:
                return {
                    "entities": {
                        labels[0]: [
                            {
                                "start": model_text.index("Cancel"),
                                "end": model_text.index("Cancel") + len("Cancel"),
                                "confidence": 0.65,
                            },
                            {
                                "start": model_text.index("Save changes"),
                                "end": model_text.index("Save changes") + len("Save changes"),
                                "confidence": 0.46,
                            },
                        ]
                    }
                }

        resolver = GlinerResolver("unused")
        resolver._model = FakeModel()

        self.assertEqual(resolver.find("save changes button", elements)[0]["id"], "e2")

    def test_rejects_a_span_outside_element_lines(self) -> None:
        self.assertIsNone(
            element_for_span(
                '@e1 button "Save"\n',
                [{"id": "e1", "role": "button", "name": "Save"}],
                {"start": 100, "end": 104, "confidence": 0.8},
            )
        )


if __name__ == "__main__":
    unittest.main()
