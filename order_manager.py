"""
餐廳訂單管理程式
本程式用於管理餐廳的訂單資料，包括新增訂單、顯示訂單報表與出餐處理，
訂單資料從 orders.json 讀取，出餐後則存入 output_orders.json。
程式符合 PEP 8 規範，且各函式均包含型別提示與 Docstring 說明。
"""

import json

# 常數定義
INPUT_FILE: str = "orders.json"
OUTPUT_FILE: str = "output_orders.json"


def load_data(filename: str) -> list:
    """
    讀取指定檔案的 JSON 資料。
    若檔案不存在或內容無法解析，則回傳空列表。

    :param filename: JSON 檔案名稱
    :return: 讀取到的訂單列表
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return []

def save_orders(filename: str, orders: list) -> None:
    """
    將訂單列表儲存成 JSON 檔案，縮排設定為 4 且支援中文顯示。

    :param filename: 要儲存的檔案名稱
    :param orders: 訂單列表
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=4, ensure_ascii=False)


def calculate_order_total(order: dict) -> int:
    """
    計算單筆訂單的總金額。

    :param order: 訂單資料（包含 items 清單）
    :return: 訂單總金額
    """
    total: int = 0
    for item in order.get("items", []):
        total += item["price"] * item["quantity"]
    return total


def print_order_report(data, title: str = "訂單報表", single: bool = False) -> None:
    """
    顯示訂單報表，支援單筆或多筆訂單的顯示。

    :param data: 單筆訂單（dict）或訂單列表（list）
    :param title: 報表標題
    :param single: 是否為單筆訂單報表
    """
    if not single:
        print("\n==================== {} ====================".format(title))
        for i, order in enumerate(data, start=1):
            print("訂單 #{}".format(i))
            print("訂單編號: {}".format(order["order_id"]))
            print("客戶姓名: {}".format(order["customer"]))
            print("--------------------------------------------------")
            print("商品名稱\t單價\t數量\t小計")
            print("--------------------------------------------------")
            for item in order["items"]:
                subtotal = item["price"] * item["quantity"]
                print(f"{item['name']}\t{item['price']}\t{item['quantity']}\t{subtotal}")
            print("--------------------------------------------------")
            total = calculate_order_total(order)
            print("訂單總額: {}".format(f"{total:,}"))
            print("==================================================\n")
    else:
        order = data
        print("\n==================== {} ====================".format(title))
        print("訂單編號: {}".format(order["order_id"]))
        print("客戶姓名: {}".format(order["customer"]))
        print("--------------------------------------------------")
        print("商品名稱\t單價\t數量\t小計")
        print("--------------------------------------------------")
        for item in order["items"]:
            subtotal = item["price"] * item["quantity"]
            print(f"{item['name']}\t{item['price']}\t{item['quantity']}\t{subtotal}")
        print("--------------------------------------------------")
        total = calculate_order_total(order)
        print("訂單總額: {}".format(f"{total:,}"))
        print("==================================================\n")


def add_order(orders: list) -> str:
    """
    新增訂單至待處理訂單列表。
    檢查訂單編號是否重複（轉為大寫後檢查），並至少需輸入一個訂單項目。
    處理價格與數量的輸入例外狀況。

    :param orders: 待處理訂單列表
    :return: 操作結果訊息
    """
    order_id: str = input("請輸入訂單編號：").strip().upper()
    # 檢查訂單編號重複
    if any(order["order_id"] == order_id for order in orders):
        return f"錯誤：訂單編號 {order_id} 已存在！"
    customer: str = input("請輸入顧客姓名：").strip()
    order_items: list = []
    while True:
        item_name: str = input("請輸入訂單項目名稱（輸入空白結束）：").strip()
        if item_name == "":
            if not order_items:
                print("=> 至少需要一個訂單項目")
                continue
            else:
                break
        # 輸入價格
        while True:
            price_input: str = input("請輸入價格：").strip()
            try:
                price: int = int(price_input)
                if price < 0:
                    print("=> 錯誤：價格不能為負數，請重新輸入")
                    continue
                break
            except ValueError:
                print("=> 錯誤：價格或數量必須為整數，請重新輸入")
        # 輸入數量
        while True:
            qty_input: str = input("請輸入數量：").strip()
            try:
                quantity: int = int(qty_input)
                if quantity <= 0:
                    print("=> 錯誤：數量必須為正整數，請重新輸入")
                    continue
                break
            except ValueError:
                print("=> 錯誤：價格或數量必須為整數，請重新輸入")
        order_items.append({"name": item_name, "price": price, "quantity": quantity})
    orders.append({
        "order_id": order_id,
        "customer": customer,
        "items": order_items
    })
    return f"訂單 {order_id} 已新增！"


def process_order(orders: list) -> tuple:
    """
    出餐處理：顯示待處理訂單列表，讓使用者選擇要出餐的訂單。
    將所選訂單從待處理訂單列表移除後加入到 output_orders.json，
    並回傳處理結果訊息與該筆訂單資料（若取消則回傳 None）。

    :param orders: 待處理訂單列表
    :return: (結果訊息, 處理的訂單或 None)
    """
    if not orders:
        return ("目前無待處理訂單", None)
    print("\n======== 待處理訂單列表 ========")
    for i, order in enumerate(orders, start=1):
        print(f"{i}. 訂單編號: {order['order_id']} - 客戶: {order['customer']}")
    print("================================")
    while True:
        choice: str = input("請選擇要出餐的訂單編號 (輸入數字或按 Enter 取消): ").strip()
        if choice == "":
            return ("取消出餐處理", None)
        if not choice.isdigit():
            print("=> 錯誤：請輸入有效的數字")
            continue
        idx: int = int(choice)
        if idx < 1 or idx > len(orders):
            print("=> 錯誤：請輸入有效的數字")
            continue
        order = orders.pop(idx - 1)
        # 將出餐訂單加入 output_orders.json
        output_orders: list = load_data(OUTPUT_FILE)
        output_orders.append(order)
        save_orders(OUTPUT_FILE, output_orders)
        msg: str = f"訂單 {order['order_id']} 已出餐完成"
        return (msg, order)


def main() -> None:
    """
    程式主流程：讀取訂單資料、提供選單功能（新增訂單、顯示報表、出餐處理、離開）。
    使用 while 迴圈控制整體流程，並適時儲存訂單資料。
    """
    orders: list = load_data(INPUT_FILE)
    while True:
        print("***************選單***************")
        print("1. 新增訂單")
        print("2. 顯示訂單報表")
        print("3. 出餐處理")
        print("4. 離開")
        print("**********************************")
        choice: str = input("請選擇操作項目(Enter 離開)：").strip()
        if choice == "" or choice == "4":
            break
        elif choice == "1":
            result: str = add_order(orders)
            print(result)
            save_orders(INPUT_FILE, orders)
        elif choice == "2":
            print_order_report(orders)
        elif choice == "3":
            result, order = process_order(orders)
            print(result)
            if order is not None:
                print("出餐訂單詳細資料：")
                print_order_report(order, title="出餐訂單", single=True)
            save_orders(INPUT_FILE, orders)
        else:
            print("=> 請輸入有效的選項（1-4）")
    print("程式結束。")


if __name__ == "__main__":
    main()
