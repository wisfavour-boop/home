#!/usr/bin/env python3
"""통상임금 계산기

2024년 대법원 판례는 통상임금 판단에서 "고정성 징표"를 더 이상 필수 요건으로 보지 않습니다.
이 프로그램은 다음 기준을 중심으로 통상임금을 계산합니다.

- 임금성 여부: 근로의 대가로 지급되는지
- 정기성 여부: 지급 규칙이 일정한지
- 통상성 여부: 통상적/일상적 근로에 대한 대가인지

고정성(금액이 항상 같아야 하는지 여부)은 참고 정보로만 사용하며,
정기성과 임금성이 인정되면 통상임금 포함 가능성을 검토합니다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class WageItem:
    name: str
    amount: float
    is_wage: bool
    is_regular: bool
    is_ordinary: bool
    is_fixed: bool

    @property
    def is_ordinary_wage(self) -> bool:
        return self.is_wage and self.is_regular and self.is_ordinary

    def explain(self) -> str:
        if self.is_ordinary_wage:
            if not self.is_fixed:
                return (
                    f"{self.name}: 통상임금 포함 가능 (정기성과 통상성 충족, 금액은 변동 가능)")
            return f"{self.name}: 통상임금 포함"
        return f"{self.name}: 통상임금 제외"


def input_yes_no(message: str) -> bool:
    while True:
        answer = input(message + " [y/n]: ").strip().lower()
        if answer in {"y", "yes", "ㅛ"}:
            return True
        if answer in {"n", "no", "ㅜ"}:
            return False
        print("y 또는 n으로 입력해주세요.")


def input_positive_float(message: str) -> float:
    while True:
        try:
            value = float(input(message).replace(",", ".").strip())
            if value < 0:
                raise ValueError
            return value
        except ValueError:
            print("숫자를 다시 입력해주세요. 예: 1200000")


def collect_wage_items() -> List[WageItem]:
    print("\n=== 통상임금 항목 입력 ===")
    print("아래 항목을 하나씩 입력하세요. 항목 이름을 비우면 입력을 종료합니다.\n")

    items: List[WageItem] = []
    index = 1
    while True:
        name = input(f"{index}. 항목명 (예: 기본급, 식대): ").strip()
        if not name:
            break

        amount = input_positive_float(f"   {name} 금액을 입력하세요: ")
        is_wage = input_yes_no("   근로의 대가인지요?")
        is_regular = input_yes_no("   매 임금 지급기간마다 지급되나요?")
        is_ordinary = input_yes_no("   통상적이고 일상적인 근로의 대가인가요?")
        is_fixed = input_yes_no("   금액이 고정되어 있나요? (2024년 판례 이후 고정성은 필수 아님)")

        items.append(
            WageItem(
                name=name,
                amount=amount,
                is_wage=is_wage,
                is_regular=is_regular,
                is_ordinary=is_ordinary,
                is_fixed=is_fixed,
            )
        )
        index += 1
        print()

    return items


def summarize_items(items: List[WageItem]) -> None:
    print("\n=== 항목 판정 결과 ===")
    for item in items:
        print(item.explain())


def compute_tongsang_imgeum(items: List[WageItem]) -> float:
    return sum(item.amount for item in items if item.is_ordinary_wage)


def calculate_overtime_rates(monthly_ordinary_wage: float) -> dict[str, float]:
    if monthly_ordinary_wage <= 0:
        return {"hourly": 0.0, "daily": 0.0, "overtime_hourly": 0.0}

    hours_per_month = 209.0
    hourly = monthly_ordinary_wage / hours_per_month
    daily = hourly * 8
    overtime_hourly = hourly * 1.5
    return {
        "hourly": hourly,
        "daily": daily,
        "overtime_hourly": overtime_hourly,
    }


def format_krw(value: float) -> str:
    return f"{value:,.0f}원"


def main() -> None:
    print("통상임금 계산기")
    print("2024년 대법원 판례에 따라 고정성 징표는 통상임금 판단의 필수 요건이 아닙니다.")
    print("정기성과 임금성, 통상성과 예측 가능성을 중심으로 계산하세요.\n")

    items = collect_wage_items()
    if not items:
        print("입력된 임금 항목이 없습니다. 프로그램을 종료합니다.")
        return

    summarize_items(items)

    ordinary_wage = compute_tongsang_imgeum(items)
    print(f"\n통상임금 합계: {format_krw(ordinary_wage)}")

    rates = calculate_overtime_rates(ordinary_wage)
    print(f"1시간 통상임금: {format_krw(rates['hourly'])}")
    print(f"1일 통상임금 (8시간 기준): {format_krw(rates['daily'])}")
    print(f"연장 1시간 수당 (1.5배): {format_krw(rates['overtime_hourly'])}")

    if input_yes_no("연장/야간/휴일 수당을 추가로 계산하시겠습니까?"):
        overtime_hours = input_positive_float("   연장근로 시간 수를 입력하세요: ")
        night_hours = input_positive_float("   야간근로 시간 수를 입력하세요: ")
        holiday_hours = input_positive_float("   휴일근로 시간 수를 입력하세요: ")

        overtime_pay = overtime_hours * rates["overtime_hourly"]
        night_pay = night_hours * rates["overtime_hourly"]
        holiday_pay = holiday_hours * rates["overtime_hourly"]
        total_extra = overtime_pay + night_pay + holiday_pay

        print("\n=== 추가 수당 계산 결과 ===")
        print(f"연장근로 수당: {format_krw(overtime_pay)}")
        print(f"야간근로 수당: {format_krw(night_pay)}")
        print(f"휴일근로 수당: {format_krw(holiday_pay)}")
        print(f"총 추가 수당: {format_krw(total_extra)}")

    print("\n계산이 완료되었습니다. 실제 판단 시에는 구체적 근로계약과 판례를 참고하세요.")


if __name__ == "__main__":
    main()
