import unittest
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import fetch_pde_discussions as fetcher


def discussion_html(canonical_url: str, question_text: str) -> str:
    return f"""
    <html>
      <head><link rel="canonical" href="{canonical_url}"></head>
      <body>
        <h1>Exam discussion</h1>
        <div>Question #: 1</div>
        <div>Topic #: 1</div>
        <div class="question-body">
          <p class="card-text">{question_text}</p>
          <ul>
            <li class="multi-choice-item correct-hidden">
              <span class="multi-choice-letter" data-choice-letter="A">A.</span>
              Correct option
            </li>
            <li class="multi-choice-item">
              <span class="multi-choice-letter" data-choice-letter="B">B.</span>
              Wrong option
            </li>
          </ul>
        </div>
      </body>
    </html>
    """


class ScanNewTests(unittest.TestCase):
    def setUp(self):
        self.original_fetch = fetcher.fetch

    def tearDown(self):
        fetcher.fetch = self.original_fetch

    def test_scan_rejects_discussion_redirected_to_another_exam(self):
        html = discussion_html(
            "https://www.examtopics.com/discussions/google/view/"
            "386533-exam-nse7_sse_ad-25-topic-1-question-1-discussion/",
            "What is the role of ZTNA tags in FortiSASE?",
        )

        fetcher.fetch = lambda url: html

        self.assertEqual(fetcher.scan_new(386532, scan_range=1, max_misses=10, delay=0), [])

    def test_scan_rejects_professional_cloud_architect_discussion(self):
        html = discussion_html(
            "https://www.examtopics.com/discussions/google/view/"
            "383615-exam-professional-cloud-architect-topic-1-question-267/",
            "You are monitoring Google Kubernetes Engine clusters.",
        )

        fetcher.fetch = lambda url: html

        self.assertEqual(fetcher.scan_new(383614, scan_range=1, max_misses=10, delay=0), [])

    def test_scan_accepts_professional_data_engineer_discussion(self):
        html = discussion_html(
            "https://www.examtopics.com/discussions/google/view/"
            "383615-exam-professional-data-engineer-topic-1-question-10/",
            "You need to design a BigQuery pipeline for streaming events.",
        )

        fetcher.fetch = lambda url: html

        questions = fetcher.scan_new(383614, scan_range=1, max_misses=10, delay=0)

        self.assertEqual(len(questions), 1)
        self.assertEqual(
            questions[0]["question_text"],
            "You need to design a BigQuery pipeline for streaming events.",
        )
        self.assertIn("professional-data-engineer", questions[0]["url"])

    def test_discover_extracts_pde_links_from_index_html(self):
        html = """
        <a class="discussion-link"
           href="/discussions/google/view/79414-exam-professional-data-engineer-topic-1-question-1/">
           PDE Q1
        </a>
        <a class="discussion-link"
           href="/discussions/google/view/7083-exam-professional-cloud-architect-topic-1-question-1/">
           PCA Q1
        </a>
        <a class="discussion-link"
           href="/discussions/google/view/385223-exam-professional-data-engineer-topic-1-question-346-discussion/">
           PDE Q346
        </a>
        """
        original_fetch = fetcher.fetch
        original_detect = fetcher.detect_discussion_index_last_page
        try:
            fetcher.detect_discussion_index_last_page = lambda delay=0.3: 1
            fetcher.fetch = lambda url: html
            questions = fetcher.discover_from_discussion_index(delay=0, max_pages=1)
        finally:
            fetcher.fetch = original_fetch
            fetcher.detect_discussion_index_last_page = original_detect

        self.assertEqual(len(questions), 2)
        self.assertEqual(
            {(q["topic"], q["question_number"]) for q in questions},
            {(1, 1), (1, 346)},
        )
        self.assertTrue(all("professional-data-engineer" in q["url"] for q in questions))

    def test_parser_extracts_year_from_comment_date_title(self):
        html = """
        <html><body>
          <div>Question #: 349</div>
          <div>Topic #: 1</div>
          <div class="question-body">
            <p class="card-text">How should you window click sessions?</p>
            <ul>
              <li class="multi-choice-item correct-hidden">
                <span class="multi-choice-letter" data-choice-letter="D">D.</span>
                Session windows
              </li>
              <li class="multi-choice-item">
                <span class="multi-choice-letter" data-choice-letter="A">A.</span>
                Tumbling windows
              </li>
            </ul>
          </div>
          <span class="comment-date align-middle" title="Sat 14 Mar 2026 13:10">
            2 months, 4 weeks ago
          </span>
        </body></html>
        """

        question = fetcher.parse_question_from_html(
            html,
            disc_id=385226,
            source_url="https://www.examtopics.com/discussions/google/view/"
            "385226-exam-professional-data-engineer-topic-1-question-349/",
        )

        self.assertIsNotNone(question)
        self.assertEqual(question["year"], 2026)

    def test_parser_extracts_year_from_abbreviated_at_date(self):
        html = """
        <html><body>
          <div>Question #: 321</div>
          <div>Topic #: 1</div>
          <div class="question-body">
            <p class="card-text">How should you govern lakes?</p>
            <ul>
              <li class="multi-choice-item correct-hidden">
                <span class="multi-choice-letter" data-choice-letter="B">B.</span>
                Dataplex
              </li>
              <li class="multi-choice-item">
                <span class="multi-choice-letter" data-choice-letter="A">A.</span>
                Custom
              </li>
            </ul>
          </div>
          <div>by 67bdb19 at <i>Jan. 16, 2026, 8:16 a.m.</i></div>
        </body></html>
        """
        question = fetcher.parse_question_from_html(
            html,
            disc_id=382517,
            source_url="https://www.examtopics.com/discussions/google/view/"
            "382517-exam-professional-data-engineer-topic-1-question-321/",
        )
        self.assertIsNotNone(question)
        self.assertEqual(question["year"], 2026)

    def test_parser_accepts_image_options_embedded_in_question_text(self):
        html = """
        <html><body>
          <div>Question #: 2</div>
          <div>Topic #: 3</div>
          <div class="question-body">
            <p class="card-text">
              Which command should you use?<br>
              A.<br><img class="in-exam-image" src="/assets/a.png"><br>
              B.<br><img class="in-exam-image" src="/assets/b.png"><br>
              C.<br><img class="in-exam-image" src="/assets/c.png"><br>
              D.<br><img class="in-exam-image" src="/assets/d.png"><br>
            </p>
          </div>
        </body></html>
        """

        question = fetcher.parse_question_from_html(
            html,
            disc_id=68709,
            source_url="https://www.examtopics.com/discussions/google/view/"
            "68709-exam-professional-data-engineer-topic-3-question-2/",
        )

        self.assertIsNotNone(question)
        self.assertEqual([o["label"] for o in question["options"]], ["A", "B", "C", "D"])
        self.assertEqual(question["options"][0]["text"], "Image: /assets/a.png")


class HtmlOutputTests(unittest.TestCase):
    def test_html_includes_year_range_filter(self):
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "questions.html"
            fetcher.build_html([
                {
                    "topic": 1,
                    "question_number": 197,
                    "year": 2024,
                    "url": "",
                    "question_text": "Recent question",
                    "options": [{"label": "A", "text": "Option"}],
                    "suggested_answer": "A",
                    "multi_answer": False,
                    "community_vote": "A (100%)",
                }
            ], str(out))

            html = out.read_text(encoding="utf-8")

        self.assertIn('id="yearFilters"', html)
        self.assertIn("2024-Now", html)
        self.assertIn("Professional Data Engineer", html)

    def test_community_vote_is_hidden_until_answer_reveal(self):
        self.assertIn("vote.classList.add('visible')", fetcher.JS)
        self.assertIn("vote.classList.remove('visible')", fetcher.JS)
        self.assertIn(".vote-box { display:none;", fetcher.CSS)
        self.assertIn(".vote-box.visible { display:block; }", fetcher.CSS)


if __name__ == "__main__":
    unittest.main()
