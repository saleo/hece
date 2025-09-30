"""
HEMouse Label Generator
Generates non-conflicting labels for UI elements
"""


class LabelGenerator:
    """Label generator with no prefix conflicts"""

    def __init__(self, charset="asdfghjkl"):
        """
        Initialize with character set
        Default: 'asdfghjkl' (home row keys, easy to type)
        Left hand: asdf
        Right hand: jkl (removed gh to avoid accidental presses)
        """
        self.charset = charset
        self.charset_size = len(charset)

    def generate_labels(self, count):
        """
        Generate non-conflicting labels

        Args:
            count: Number of labels to generate

        Returns:
            List of label strings
        """
        if count <= 0:
            return []

        labels = []

        # Stage 1: Single letters ONLY (up to 9 elements)
        if count <= self.charset_size:
            return [self.charset[i] for i in range(count)]

        # Stage 2: Two-letter combinations ONLY (no single letters to avoid prefix conflicts)
        # For 10+ elements, we skip single letters entirely
        left_hand = "asdf"
        right_hand = "jkl"

        # Prioritize left-right or right-left alternations
        for c1 in self.charset:
            for c2 in self.charset:
                if len(labels) >= count:
                    return labels[:count]

                # Prefer alternating hands
                if (c1 in left_hand and c2 in right_hand) or \
                   (c1 in right_hand and c2 in left_hand):
                    label = c1 + c2
                    if label not in labels:
                        labels.append(label)

        # If still need more, add same-hand combinations
        for c1 in self.charset:
            for c2 in self.charset:
                if len(labels) >= count:
                    return labels[:count]
                label = c1 + c2
                if label not in labels:
                    labels.append(label)

        # If still need more, add three-letter combinations
        if len(labels) < count:
            for c1 in self.charset:
                for c2 in self.charset:
                    for c3 in self.charset:
                        if len(labels) >= count:
                            return labels[:count]
                        label = c1 + c2 + c3
                        if label not in labels:
                            labels.append(label)

        return labels[:count]

    def match_label(self, input_str, labels):
        """
        Match user input against labels

        Args:
            input_str: User's input string
            labels: List of available labels

        Returns:
            List of matching label indices
        """
        matches = []
        for i, label in enumerate(labels):
            if label.startswith(input_str):
                matches.append(i)
        return matches

    def verify_no_prefix_conflicts(self, labels):
        """
        Verify that no label is a prefix of another

        Args:
            labels: List of labels to check

        Returns:
            True if no conflicts, False otherwise
        """
        for i, label1 in enumerate(labels):
            for j, label2 in enumerate(labels):
                if i != j and label2.startswith(label1):
                    return False
        return True


# Test code
if __name__ == "__main__":
    gen = LabelGenerator()

    # Test 1: Single letters (9 elements)
    print("Test 1: 9 elements")
    labels = gen.generate_labels(9)
    print(f"Labels: {labels}")
    assert labels == ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l']
    print("✅ Single letters test passed\n")

    # Test 2: Two letters (20 elements)
    print("Test 2: 20 elements")
    labels = gen.generate_labels(20)
    print(f"Labels: {labels}")
    print(f"✅ Generated {len(labels)} labels\n")

    # Test 3: No prefix conflicts
    print("Test 3: Prefix conflict check")
    labels = gen.generate_labels(50)
    if gen.verify_no_prefix_conflicts(labels):
        print("✅ No prefix conflicts found\n")
    else:
        print("❌ Prefix conflicts detected!\n")

    # Test 4: Matching
    print("Test 4: Label matching")
    labels = gen.generate_labels(20)
    matches = gen.match_label("a", labels)
    print(f"Input 'a' matches: {[labels[i] for i in matches]}")
    matches = gen.match_label("as", labels)
    print(f"Input 'as' matches: {[labels[i] for i in matches]}")
    print("✅ Matching test passed")