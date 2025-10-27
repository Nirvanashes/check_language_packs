import flet as ft
from flet.core.file_picker import FilePickerFileType
import check_language_packs as clp


def main(page: ft.Page):
    title = ft.Text(
        value="JSON语言包Key比较工具，用于比较两个JSON文件中的key差异", color="green"
    )

    prog_bars: Dict[str, ft.ProgressRing] = {}
    files = ft.Ref[ft.Column]()
    check_button = ft.Ref[ft.ElevatedButton]()

    def file_picker_result(e: ft.FilePickerResultEvent):
        check_button.current.disabled = True if e.files is None else False
        prog_bars.clear()
        files.current.controls.clear()
        if e.files is not None:
            for f in e.files:
                prog = ft.ProgressRing(value=0, bgcolor="#eeeeee", width=20, height=20)
                prog_bars[f.name] = prog
                files.current.controls.append(ft.Row([prog, ft.Text(f.name)]))
        page.update()

    def on_upload_progress(e: ft.FilePickerUploadEvent):
        prog_bars[e.file_name].value = e.progress
        prog_bars[e.file_name].update()

    file_picker = ft.FilePicker(
        on_result=file_picker_result, on_upload=on_upload_progress
    )

    def upload_files(e):
        uf = []
        if file_picker.result is not None and file_picker.result.files is not None:
            for f in file_picker.result.files:
                uf.append(
                    ft.FilePickerUploadFile(
                        f.name,
                        upload_url=page.get_upload_url(f.name, 60),
                    )
                )
            file_picker.upload(uf)


    # hide dialog in a overlay
    page.overlay.append(file_picker)

    page.add(
        ft.ElevatedButton(
            "Select files...",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=lambda _: file_picker.pick_files(allow_multiple=True,allowed_extensions=["json"]),
        ),
        ft.Column(ref=files),
        ft.ElevatedButton(
            "Check File",
            ref=check_button,
            icon=ft.Icons.UPLOAD,
            on_click=upload_files,
            disabled=True,
        ),
        ft.ElevatedButton(
            "Save File",
            icon=ft.Icons.SAVE,
            on_click=lambda _: file_picker.save_file(dialog_title="保存文件",file_name="check_result.json")
        )
    )


ft.app(main,upload_dir="uploads")
