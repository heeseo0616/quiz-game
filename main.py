import json

STATE_FILE = "state.json"


# ============================================================
# 공용 함수 (게임 상태와 무관한 도구)
# ============================================================

def ask_number(prompt, min_value, max_value):
    """min_value ~ max_value 범위의 정수를 받을 때까지 반복해서 물어본다."""
    while True:
        raw = input(prompt).strip()

        if raw == "":
            print(f"입력이 비어 있습니다. {min_value}~{max_value} 사이의 숫자를 입력하세요.")
            continue

        try:
            number = int(raw)
        except ValueError:
            print(f"숫자가 아닙니다. {min_value}~{max_value} 사이의 숫자를 입력하세요.")
            continue

        if number < min_value or number > max_value:
            print(f"{min_value}~{max_value} 사이의 숫자를 입력하세요.")
            continue

        return number


def ask_text(prompt):
    """비어 있지 않은 문자열을 받을 때까지 반복해서 물어본다."""
    while True:
        raw = input(prompt).strip()

        if raw == "":
            print("내용을 입력해 주세요.")
            continue

        return raw


def score_percent(correct, total):
    """맞힌 개수와 총 문제 수로 100점 만점 점수를 계산한다."""
    if total == 0:
        return 0
    return int(correct / total * 100)


# ============================================================
# Quiz : 퀴즈 한 문제를 표현하는 클래스
# ============================================================

class Quiz:

    def __init__(self, question, choices, answer):
        self.question = question    # str  : 문제 텍스트
        self.choices = choices      # list : 선택지 4개
        self.answer = answer        # int  : 정답 번호 1~4

    def show(self, number):
        """문제 번호, 문제, 선택지를 화면에 출력한다."""
        print(f"\n[문제 {number}]")
        print(self.question)
        print()
        for index, choice in enumerate(self.choices):
            print(f"{index + 1}. {choice}")

    def is_correct(self, user_answer):
        """받은 번호가 정답이면 True를 반환한다."""
        return user_answer == self.answer

    def to_dict(self):
        """JSON에 저장할 수 있는 dict 형태로 변환한다."""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @staticmethod
    def from_dict(data):
        """dict에서 Quiz 객체를 만들어 반환한다. (to_dict의 반대)"""
        return Quiz(data["question"], data["choices"], data["answer"])


# ============================================================
# QuizGame : 게임 전체를 관리하는 클래스
# ============================================================

class QuizGame:

    def __init__(self):
        self.quizzes = []       # list[Quiz] : 등록된 퀴즈 전체
        self.best_score = 0     # int : 최고 기록에서 맞힌 개수
        self.best_total = 0     # int : 그때 푼 문제 수 (0이면 아직 안 풂)
        self.load()

    # ---------- 데이터 ----------

    def default_quizzes(self):
        """파일이 없거나 손상됐을 때 사용할 기본 수학 퀴즈 5개."""
        return [
            Quiz("15 + 27 = ?", ["32", "42", "52", "45"], 2),
            Quiz("8 × 7 = ?", ["54", "56", "64", "48"], 2),
            Quiz("100 - 37 = ?", ["63", "73", "53", "67"], 1),
            Quiz("45 ÷ 9 = ?", ["4", "5", "6", "7"], 2),
            Quiz("12 + 3 × 4 = ?", ["60", "24", "19", "48"], 2),
        ]

    def load(self):
        """state.json에서 퀴즈와 최고 점수를 불러온다."""
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
            self.best_score = data["best_score"]
            self.best_total = data["best_total"]

            if self.best_total > 0:
                percent = score_percent(self.best_score, self.best_total)
                print(f"저장된 데이터를 불러왔습니다. "
                      f"(퀴즈 {len(self.quizzes)}개, 최고점수 {percent}점)")
            else:
                print(f"저장된 데이터를 불러왔습니다. "
                      f"(퀴즈 {len(self.quizzes)}개, 최고점수 기록 없음)")

        except FileNotFoundError:
            self.quizzes = self.default_quizzes()
            print("저장된 데이터가 없어 기본 퀴즈로 시작합니다.")

        except (json.JSONDecodeError, KeyError, TypeError):
            self.quizzes = self.default_quizzes()
            self.best_score = 0
            self.best_total = 0
            print("데이터 파일이 손상되어 기본 퀴즈로 초기화합니다.")

    def save(self):
        """퀴즈와 최고 점수를 state.json에 저장한다."""
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "best_total": self.best_total,
        }

        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError:
            print("데이터를 저장하지 못했습니다.")

    # ---------- 화면 ----------

    def show_menu(self):
        """메뉴를 출력한다."""
        print("\n" + "=" * 40)
        print("         수학 암산 퀴즈 게임 ")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print("=" * 40)

    def play_quiz(self):
        """퀴즈를 출제하고 채점한 뒤 최고 점수를 갱신한다."""
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        total = len(self.quizzes)
        print(f"\n퀴즈를 시작합니다! (총 {total}문제)")

        score = 0
        for index, quiz in enumerate(self.quizzes):
            print("\n" + "-" * 40)
            quiz.show(index + 1)

            user_answer = ask_number("\n정답 입력 (1-4): ", 1, 4)

            if quiz.is_correct(user_answer):
                print("정답입니다!")
                score += 1
            else:
                print(f"오답입니다! 정답은 {quiz.answer}번입니다.")

        percent = score_percent(score, total)
        best_percent = score_percent(self.best_score, self.best_total)

        print("\n" + "=" * 40)
        print(f"🏆 결과: {total}문제 중 {score}문제 정답! ({percent}점)")

        if self.best_total == 0 or percent > best_percent:
            self.best_score = score
            self.best_total = total
            print("새로운 최고 점수입니다!")

        print("=" * 40)
        self.save()

    def add_quiz(self):
        """새 퀴즈를 입력받아 등록하고 파일에 저장한다."""
        print("\n새로운 퀴즈를 추가합니다.")

        question = ask_text("문제를 입력하세요: ")

        choices = []
        for i in range(1, 5):
            choice = ask_text(f"선택지 {i}: ")
            choices.append(choice)

        answer = ask_number("정답 번호 (1-4): ", 1, 4)

        self.quizzes.append(Quiz(question, choices, answer))
        self.save()
        print("\n✅ 퀴즈가 추가되었습니다!")

    def show_list(self):
        """등록된 퀴즈 목록을 출력한다."""
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다.")
            return

        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("-" * 40)
        for index, quiz in enumerate(self.quizzes):
            print(f"[{index + 1}] {quiz.question}")
        print("-" * 40)

    def show_score(self):
        """최고 점수를 출력한다."""
        if self.best_total == 0:
            print("\n아직 퀴즈를 풀지 않았습니다.")
            return

        percent = score_percent(self.best_score, self.best_total)
        print(f"\n최고 점수: {percent}점 "
              f"({self.best_total}문제 중 {self.best_score}문제 정답)")

    # ---------- 메인 루프 ----------

    def run(self):
        """메뉴를 반복 출력하며 사용자의 선택을 처리한다."""
        while True:
            self.show_menu()
            choice = ask_number("선택: ", 1, 5)

            if choice == 1:
                self.play_quiz()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.show_list()
            elif choice == 4:
                self.show_score()
            elif choice == 5:
                self.save()
                print("\n게임을 종료합니다. 안녕히 가세요!")
                break


# ============================================================
# 진입점
# ============================================================

if __name__ == "__main__":
    game = QuizGame()
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        print("\n\n입력이 중단되었습니다. 저장 후 종료합니다.")
        game.save()