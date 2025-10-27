import flet as ft


def main(page: ft.Page):
    title = ft.Text(value="JSON语言包Key比较工具，用于比较两个JSON文件中的key差异", color="green")
    counter = ft.Text("0", size=50, data=0)
    file1 = ft.

    def increment_click(e):
        counter.data += 1
        counter.value = str(counter.data)
        counter.update()

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD, on_click=increment_click
    )
    page.add(
        ft.SafeArea(
            title,
            ft.Container(
                # title,
                counter,
                alignment=ft.alignment.center,
            ),
            expand=True,
        )
    )


ft.app(main)
