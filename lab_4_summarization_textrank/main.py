"""
Lab 4
Summarize text using TextRank algorithm
"""
from typing import Union, Any
import re

from lab_3_keywords_textrank.main import TextEncoder, \
    TextPreprocessor

PreprocessedSentence = tuple[str, ...]
EncodedSentence = tuple[int, ...]


def check_sequence(sequence: Any, seq_type: Any, element_type: Any) -> None:
    """
    Checks the types of variables. In case of wrong type raises ValueError
    """
    if not isinstance(sequence, seq_type):
        raise ValueError
    for element in sequence:
        if not isinstance(element, element_type):
            raise ValueError


class Sentence:
    """
    An abstraction over the real-world sentences
    """

    def __init__(self, text: str, position: int) -> None:
        """
        Constructs all the necessary attributes
        """
        if not isinstance(text, str) or isinstance(position, bool) or not isinstance(position, int):
            raise ValueError
        self._text = text
        self._position = position
        self._preprocessed: tuple[str, ...] = ()
        self._encoded: tuple[int, ...] = ()

    def get_position(self) -> int:
        """
        Returns the attribute
        :return: the position of the sentence in the text
        """
        return self._position

    def set_text(self, text: str) -> None:
        """
        Sets the attribute
        :param text: the text
        :return: None
        """
        if not isinstance(text, str):
            raise ValueError
        self._text = text

    def get_text(self) -> str:
        """
        Returns the attribute
        :return: the text
        """
        return self._text

    def set_preprocessed(self, preprocessed_sentence: PreprocessedSentence) -> None:
        """
        Sets the attribute
        :param preprocessed_sentence: the preprocessed sentence (a sequence of tokens)
        :return: None
        """
        check_sequence(preprocessed_sentence, tuple, str)
        self._preprocessed = preprocessed_sentence

    def get_preprocessed(self) -> PreprocessedSentence:
        """
        Returns the attribute
        :return: the preprocessed sentence (a sequence of tokens)
        """
        return self._preprocessed

    def set_encoded(self, encoded_sentence: EncodedSentence) -> None:
        """
        Sets the attribute
        :param encoded_sentence: the encoded sentence (a sequence of numbers)
        :return: None
        """
        check_sequence(encoded_sentence, tuple, int)
        self._encoded = encoded_sentence

    def get_encoded(self) -> EncodedSentence:
        """
        Returns the attribute
        :return: the encoded sentence (a sequence of numbers)
        """
        return self._encoded


class SentencePreprocessor(TextPreprocessor):
    """
    Class for sentence preprocessing
    """

    def __init__(self, stop_words: tuple[str, ...], punctuation: tuple[str, ...]) -> None:
        """
        Constructs all the necessary attributes
        """
        check_sequence(stop_words, tuple, str)
        check_sequence(punctuation, tuple, str)
        super().__init__(stop_words, punctuation)

    def _split_by_sentence(self, text: str) -> tuple[Sentence, ...]:
        """
        Splits the provided text by sentence
        :param text: the raw text
        :return: a sequence of sentences
        """
        if not isinstance(text, str):
            raise ValueError
        text = text.replace("\n", " ").replace("  ", " ")
        sentences = re.split(r'(?<=[?!.])\s+(?=[А-ЯA-Z])', text)
        list_of_sentences = []
        for index, sentence in enumerate(sentences):
            list_of_sentences.append(Sentence(sentence, index))
        return tuple(list_of_sentences)

    def _preprocess_sentences(self, sentences: tuple[Sentence, ...]) -> None:
        """
        Enriches the instances of sentences with their preprocessed versions
        :param sentences: a list of sentences
        :return:
        """
        check_sequence(sentences, tuple, Sentence)
        for sentence in sentences:
            text = sentence.get_text()
            processed_sentence = super().preprocess_text(text)
            sentence.set_preprocessed(processed_sentence)

    def get_sentences(self, text: str) -> tuple[Sentence, ...]:
        """
        Extracts the sentences from the given text & preprocesses them
        :param text: the raw text
        :return:
        """
        if not isinstance(text, str):
            raise ValueError
        split_sentences = self._split_by_sentence(text)
        self._preprocess_sentences(split_sentences)
        return split_sentences


class SentenceEncoder(TextEncoder):
    """
    A class to encode string sequence into matching integer sequence
    """

    def __init__(self) -> None:
        """
        Constructs all the necessary attributes
        """
        super().__init__()
        self._last_id = 1000

    def _learn_indices(self, tokens: tuple[str, ...]) -> None:
        """
        Fills attributes mapping words and integer equivalents to each other
        :param tokens: a sequence of string tokens
        :return:
        """
        check_sequence(tokens, tuple, str)
        for token in tokens:
            if token not in self._word2id.keys():
                self._word2id[token] = self._last_id
                self._id2word[self._last_id] = token
                self._last_id += 1

    def encode_sentences(self, sentences: tuple[Sentence, ...]) -> None:
        """
        Enriches the instances of sentences with their encoded versions
        :param sentences: a sequence of sentences
        :return: a list of sentences with their preprocessed versions
        """
        check_sequence(sentences, tuple, Sentence)
        for sentence in sentences:
            encoded_list = []
            preprocessed_sentence = sentence.get_preprocessed()
            self._learn_indices(preprocessed_sentence)
            for word in preprocessed_sentence:
                encoded_list.append(self._word2id[word])
            sentence.set_encoded(tuple(encoded_list))


def calculate_similarity(sequence: Union[list, tuple], other_sequence: Union[list, tuple]) -> float:
    """
    Calculates similarity between two sequences using Jaccard index
    :param sequence: a sequence of items
    :param other_sequence: a sequence of items
    :return: similarity score
    """
    if not isinstance(sequence, (list, tuple)) or not isinstance(other_sequence, (list, tuple)):
        raise ValueError
    if not sequence or not other_sequence:
        return 0
    return len(set(sequence).intersection(set(other_sequence)))/len(set(sequence).union(set(other_sequence)))


class SimilarityMatrix:
    """
    A class to represent relations between sentences
    """

    _matrix: list[list[float]]

    def __init__(self) -> None:
        """
        Constructs necessary attributes
        """
        self._matrix = []
        self._vertices = []

    def get_vertices(self) -> tuple[Sentence, ...]:
        """
        Returns a sequence of all vertices present in the graph
        :return: a sequence of vertices
        """
        return tuple(self._vertices)

    def calculate_inout_score(self, vertex: Sentence) -> int:
        """
        Retrieves a number of vertices that are similar (i.e. have similarity score > 0) to the input one
        :param vertex
        :return:
        """
        if not isinstance(vertex, Sentence):
            raise ValueError
        if vertex not in self._vertices:
            raise ValueError
        inout_score = sum(score > 0 for score in self._matrix[self._vertices.index(vertex)]) - 1
        return inout_score

    def add_edge(self, vertex1: Sentence, vertex2: Sentence) -> None:
        """
        Adds or overwrites an edge in the graph between the specified vertices
        :param vertex1:
        :param vertex2:
        :return:
        """
        if not (isinstance(vertex1, Sentence) or isinstance(vertex2, Sentence)):
            raise ValueError
        if vertex1 == vertex2:
            raise ValueError

        for vertex in vertex1, vertex2:
            if vertex in self._vertices:
                continue
            self._vertices.append(vertex)
            for element in self._matrix:
                element.append(0)
            self._matrix.append([0 for _ in self._vertices])

        index1 = self._vertices.index(vertex1)
        index2 = self._vertices.index(vertex2)
        self._matrix[index1][index2] = calculate_similarity(vertex1.get_encoded(), vertex2.get_encoded())
        self._matrix[index2][index1] = calculate_similarity(vertex2.get_encoded(), vertex1.get_encoded())
        self._matrix[index1][index1] = self._matrix[index2][index2] = 1

    def get_similarity_score(self, sentence: Sentence, other_sentence: Sentence) -> float:
        """
        Gets the similarity score for two sentences from the matrix
        :param sentence
        :param other_sentence
        :return: the similarity score
        """
        if not (isinstance(sentence, Sentence) or isinstance(other_sentence, Sentence)):
            raise ValueError
        if sentence not in self._vertices or other_sentence not in self._vertices:
            raise ValueError

        return self._matrix[self._vertices.index(sentence)][self._vertices.index(other_sentence)]

    def fill_from_sentences(self, sentences: tuple[Sentence, ...]) -> None:
        """
        Updates graph instance with vertices and edges extracted from sentences
        :param sentences
        :return:
        """
        check_sequence(sentences, tuple, Sentence)
        if not sentences:
            raise ValueError
        for sentence1 in sentences:
            for sentence2 in sentences:
                if sentence1.get_encoded() == sentence2.get_encoded():
                    break
                self.add_edge(sentence1, sentence2)


class TextRankSummarizer:
    """
    TextRank for summarization
    """

    _scores: dict[Sentence, float]
    _graph: SimilarityMatrix

    def __init__(self, graph: SimilarityMatrix) -> None:
        """
        Constructs all the necessary attributes
        :param graph: the filled instance of the similarity matrix
        """
        if not isinstance(graph, SimilarityMatrix):
            raise ValueError
        self._graph = graph
        self._damping_factor = 0.85
        self._convergence_threshold = 0.0001
        self._max_iter = 50
        self._scores = {}

    def update_vertex_score(
            self, vertex: Sentence, incidental_vertices: list[Sentence], scores: dict[Sentence, float]
    ) -> None:
        """
        Changes vertex significance score using algorithm-specific formula
        :param vertex: a sentence
        :param incidental_vertices: vertices with similarity score > 0 for vertex
        :param scores: current vertices scores
        :return:
        """
        if not (isinstance(vertex, Sentence) or isinstance(scores, dict)):
            raise ValueError
        check_sequence(incidental_vertices, list, Sentence)
        self._scores[vertex] = (1 - self._damping_factor) + self._damping_factor * \
        sum(self._scores[incidental_vertex] / (1 + self._graph.calculate_inout_score(incidental_vertex))
            for incidental_vertex in incidental_vertices)


    def train(self) -> None:
        """
        Iteratively computes significance scores for vertices
        """
        vertices = self._graph.get_vertices()
        for vertex in vertices:
            self._scores[vertex] = 1.0

        for iteration in range(self._max_iter):
            prev_score = self._scores.copy()
            for scored_vertex in vertices:
                similar_vertices = [vertex for vertex in vertices
                                    if self._graph.get_similarity_score(scored_vertex, vertex) > 0]
                self.update_vertex_score(scored_vertex, similar_vertices, prev_score)
            abs_score_diff = [abs(i - j) for i, j in zip(prev_score.values(), self._scores.values())]

            if sum(abs_score_diff) <= self._convergence_threshold:  # convergence condition
                print("Converging at iteration " + str(iteration) + "...")
                break

    def get_top_sentences(self, n_sentences: int) -> tuple[Sentence, ...]:
        """
        Retrieves top n most important sentences in the encoded text
        :param n_sentences: number of sentence to retrieve
        :return: a sequence of sentences
        """
        if not isinstance(n_sentences, int) or isinstance(n_sentences, bool):
            raise ValueError
        return tuple(sorted(self._scores, key=lambda x: self._scores[x], reverse=True)[:n_sentences])

    def make_summary(self, n_sentences: int) -> str:
        """
        Constructs summary from the most important sentences
        :param n_sentences: number of sentences to include in the summary
        :return: summary
        """
        if not isinstance(n_sentences, int) or isinstance(n_sentences, bool):
            raise ValueError
        top = sorted(self.get_top_sentences(n_sentences), key=lambda x: x.get_position())
        return '\n'.join(sentence.get_text() for sentence in top)


class Buddy:
    """
    (Almost) All-knowing entity
    """

    def __init__(
            self,
            paths_to_texts: list[str],
            stop_words: tuple[str, ...],
            punctuation: tuple[str, ...],
            idf_values: dict[str, float],
    ):
        """
        Constructs all the necessary attributes
        :param paths_to_texts: paths to the texts from which to learn
        :param stop_words: a sequence of stop words
        :param punctuation: a sequence of punctuation symbols
        :param idf_values: pre-computed IDF values
        """
        pass

    def add_text_to_database(self, path_to_text: str) -> None:
        """
        Adds the given text to the existing database
        :param path_to_text
        :return:
        """
        pass

    def _find_texts_close_to_keywords(self, keywords: tuple[str, ...], n_texts: int) -> tuple[str, ...]:
        """
        Finds texts that are similar (i.e. contain the same keywords) to the given keywords
        :param keywords: a sequence of keywords
        :param n_texts: number of texts to find
        :return: the texts' ids
        """
        pass

    def reply(self, query: str, n_summaries: int = 3) -> str:
        """
        Replies to the query
        :param query: the query
        :param n_summaries: the number of summaries to include in the answer
        :return: the answer
        """
        pass
