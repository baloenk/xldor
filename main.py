import sys
import app.config  # Load environment variables first
from app.menus.util import clear_screen, pause, print_header, Style, ascii_art
from app.client.engsel import *
from app.service.auth import AuthInstance
from app.menus.bookmark import show_bookmark_menu
from app.menus.account import show_account_menu
from app.menus.package import fetch_my_packages, get_packages_by_family, show_package_details
from app.menus.family_bookmark import show_family_bookmark_menu
from app.menus.bundle import show_bundle_menu
from app.menus.hot import show_hot_menu, show_hot_menu2
from app.menus.points import run_point_exchange
from app.service.sentry import enter_sentry_mode

def show_main_menu(number, balance, balance_expired_at, display_quota=None):
    clear_screen()
    phone_number = number
    remaining_balance = balance
    expired_at = balance_expired_at
    expired_at_dt = datetime.fromtimestamp(expired_at).strftime("%Y-%m-%d %H:%M:%S")

    print_header("✨ MENU UTAMA ✨") 
    print(f"  {Style.GREEN}👤 Akun Aktif : {phone_number}{Style.RESET}")
    print(f"  {Style.YELLOW}💰 Sisa Pulsa : Rp {remaining_balance}{Style.RESET}")
    if display_quota:
        print(f"  {Style.CYAN}📊 Sisa Kuota : {display_quota}{Style.RESET}")
    print(f"  {Style.BLUE}⏳ Masa Aktif : {expired_at_dt}{Style.RESET}")
    
    print(f"{'-'*55}")
    print(f"  {Style.BOLD}Pilih Menu:{Style.RESET}")
    print(f"  {Style.CYAN}[1]{Style.RESET}. 👤 Login / Ganti Akun")
    print(f"  {Style.CYAN}[2]{Style.RESET}. 📦 Lihat Paket Saya")
    print(f"  {Style.CYAN}[3]{Style.RESET}. 🔥 Beli Paket Hot Promo")
    print(f"  {Style.CYAN}[4]{Style.RESET}. ♨️ Beli Paket Hot Promo 2 (Bundling)")
    print(f"  {Style.CYAN}[5]{Style.RESET}. 🔍 Beli Paket Berdasarkan Family Code")
    print(f"  {Style.CYAN}[6]{Style.RESET}. 🛒 Beli Paket Bundle (Multi)")
    print(f"  {Style.CYAN}[7]{Style.RESET}. 📚 Bookmark Family Code")
    print(f"  {Style.CYAN}[8]{Style.RESET}. 🎁 Tukar Poin")
    print(f"  {Style.CYAN}[0]{Style.RESET}. 🔖 Lihat Bookmark Paket")
    print(f"  {Style.CYAN}[99]{Style.RESET}. 🚪 Keluar Aplikasi")
    print(f"{'-'*55}")

show_menu = True
def main():
    
    if ascii_art:
        ascii_art.to_terminal(columns=55)

    while True:
        active_user = AuthInstance.get_active_user()

        # Logged in
        if active_user is not None:
            try:
                balance = get_balance(AuthInstance.api_key, active_user["tokens"]["id_token"])
                if balance is None:
                    print("Gagal mengambil data saldo.")
                    pause()
                    continue
                balance_remaining = balance.get("remaining", 0)
                balance_expired_at = balance.get("expired_at", 0)
            except Exception as e:
                print(f"Gagal mengambil data saldo: {e}")
                pause()
                continue

            try:
                quota = get_main_quota(AuthInstance.api_key, active_user["tokens"]["id_token"]) or {}
                remaining = quota.get("remaining", 0)
                total = quota.get("total", 0)
                has_unlimited = quota.get("has_unlimited", False)
                remaining_gb = remaining / 1e9
                total_gb = total / 1e9
                if (total > 0) or has_unlimited:
                    display_quota = (
                        f"{remaining_gb:.2f} GB / {total_gb:.2f} GB (Unlimited)"
                        if has_unlimited
                        else f"{remaining_gb:.2f} GB / {total_gb:.2f} GB"
                    )
                else:
                    display_quota = None
            except Exception as e:
                display_quota = None
                print(f"Gagal mengambil data kuota: {e}")

            show_main_menu(active_user["number"], balance_remaining, balance_expired_at, display_quota)

            choice = input("Pilihan > ")
            if choice == "1":
                show_account_menu()
                continue
            elif choice == "2":
                fetch_my_packages()
                continue
            elif choice == "3":
                show_hot_menu()
            elif choice == "4":
                show_hot_menu2()
            elif choice == "5":
                family_code = input("Enter family code (or '99' to cancel): ")
                if family_code == "99":
                    continue
                get_packages_by_family(family_code)
            elif choice == "6":
                show_bundle_menu()
            elif choice == "7":
                show_family_bookmark_menu()
            elif choice == "8":
                run_point_exchange(active_user["tokens"])
            elif choice == "0":
                show_bookmark_menu()
            elif choice == "99":
                print("Exiting the application.")
                sys.exit(0)
            elif choice == "t":
                res = get_package(
                    AuthInstance.api_key,
                    active_user["tokens"],
                    ""
                )
                print(json.dumps(res, indent=2))
                input("Press Enter to continue...")
                pass
            elif choice == "s":
                enter_sentry_mode()
            else:
                print("Invalid choice. Please try again.")
                pause()
        else:
            # Not logged in
            show_account_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting the application.")
    # except Exception as e:
    #     print(f"An error occurred: {e}")
