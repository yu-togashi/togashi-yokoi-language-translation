from localgw.data import load_dictionary, load_vectors


def test_load_vectors_skips_malformed_and_duplicates(tmp_path):
    p = tmp_path / "toy.vec"
    p.write_text("5 3\n"
                 "a 1 2 3\n"
                 "b c 1 2 3\n"   # token with a space -> malformed
                 "a 4 5 6\n"     # duplicate
                 "d 7 8 9 \n"    # trailing space is fine
                 "e 1 1 1\n")
    words, vecs, stats = load_vectors("xx", path=p)
    assert words == ["a", "d", "e"]
    assert vecs.shape == (3, 3)
    assert vecs[1].tolist() == [7, 8, 9]
    assert stats["n_malformed"] == 1 and stats["n_duplicate"] == 1

    words, _, _ = load_vectors("xx", max_words=2, path=p)
    assert words == ["a", "d"]


def test_load_dictionary_one_to_many(tmp_path):
    p = tmp_path / "toy.txt"
    p.write_text("cat gato\ncat gata\ncat gato\ndog perro\n")
    d = load_dictionary("en", "es", "5000-6500", path=p)
    assert d == {"cat": ["gato", "gata"], "dog": ["perro"]}
