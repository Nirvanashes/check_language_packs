import flet as ft
import json
from pathlib import Path
from typing import Dict, Set, Tuple
import tempfile
import os


class JSONComparatorApp:
    def __init__(self):
        self.file1_path = None
        self.file2_path = None
        self.file_picker = ft.FilePicker()
        self.pick_files_dialog = ft.FilePicker()
        self.save_file_dialog = ft.FilePicker()

    def extract_keys(self, data: Dict, prefix: str = "") -> Set[str]:
        """
        递归提取JSON中的所有key，支持嵌套结构
        """
        keys = set()

        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                # 递归处理嵌套字典
                nested_keys = self.extract_keys(value, full_key)
                keys.update(nested_keys)
            else:
                keys.add(full_key)

        return keys

    def load_json_from_file(self, file_path: str) -> Dict:
        """
        从文件路径加载JSON数据
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"加载JSON文件失败: {e}")

    def compare_json_files(
        self, file1_path: str, file2_path: str
    ) -> Tuple[Set[str], Set[str], Set[str]]:
        """
        比较两个JSON文件的key
        """
        data1 = self.load_json_from_file(file1_path)
        data2 = self.load_json_from_file(file2_path)

        keys1 = self.extract_keys(data1)
        keys2 = self.extract_keys(data2)

        only_in_file1 = keys1 - keys2
        only_in_file2 = keys2 - keys1
        common_keys = keys1 & keys2

        return only_in_file1, only_in_file2, common_keys

    def save_comparison_report(
        self,
        file1_name: str,
        file2_name: str,
        only_in_file1: Set[str],
        only_in_file2: Set[str],
        common_keys: Set[str],
        save_path: str,
    ):
        """
        保存比较报告到文件
        """
        report_lines = []
        report_lines.append(f"JSON Key 比较报告: {file1_name} vs {file2_name}")
        report_lines.append("=" * 50)
        report_lines.append("")

        # 统计信息
        report_lines.append("统计信息:")
        report_lines.append(
            f"  {file1_name} 总key数: {len(only_in_file1) + len(common_keys)}"
        )
        report_lines.append(
            f"  {file2_name} 总key数: {len(only_in_file2) + len(common_keys)}"
        )
        report_lines.append(f"  共有key数: {len(common_keys)}")
        report_lines.append(f"  仅存在于 {file1_name} 的key数: {len(only_in_file1)}")
        report_lines.append(f"  仅存在于 {file2_name} 的key数: {len(only_in_file2)}")
        report_lines.append("")

        # 仅存在于file1的key
        if only_in_file1:
            report_lines.append(f"仅存在于 {file1_name} 的key:")
            report_lines.append("-" * 40)
            for key in sorted(only_in_file1):
                report_lines.append(f"  {key}")
            report_lines.append("")

        # 仅存在于file2的key
        if only_in_file2:
            report_lines.append(f"仅存在于 {file2_name} 的key:")
            report_lines.append("-" * 40)
            for key in sorted(only_in_file2):
                report_lines.append(f"  {key}")

        with open(save_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

    def main(self, page: ft.Page):
        # 页面设置
        page.title = "JSON语言包比较工具"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        page.scroll = ft.ScrollMode.ADAPTIVE

        # 存储上传的文件引用
        file1_ref = ft.Ref[ft.Text]()
        file2_ref = ft.Ref[ft.Text]()
        result_ref = ft.Ref[ft.Column]()
        progress_ref = ft.Ref[ft.ProgressBar]()

        def on_file1_selected(e: ft.FilePickerResultEvent):
            if e.files:
                self.file1_path = e.files[0].path
                file1_ref.current.value = f"文件1: {e.files[0].name}"
                file1_ref.current.color = ft.Colors.GREEN
            else:
                file1_ref.current.value = "文件1: 未选择"
                file1_ref.current.color = ft.Colors.RED
            page.update()

        def on_file2_selected(e: ft.FilePickerResultEvent):
            if e.files:
                self.file2_path = e.files[0].path
                file2_ref.current.value = f"文件2: {e.files[0].name}"
                file2_ref.current.color = ft.Colors.GREEN
            else:
                file2_ref.current.value = "文件2: 未选择"
                file2_ref.current.color = ft.Colors.RED
            page.update()

        def on_save_result(e: ft.FilePickerResultEvent):
            if e.path:
                try:
                    # 获取比较结果
                    only_in_file1, only_in_file2, common_keys = self.compare_json_files(
                        self.file1_path, self.file2_path
                    )

                    # 保存报告
                    file1_name = Path(self.file1_path).name
                    file2_name = Path(self.file2_path).name
                    self.save_comparison_report(
                        file1_name,
                        file2_name,
                        only_in_file1,
                        only_in_file2,
                        common_keys,
                        e.path,
                    )

                    page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text(f"报告已保存到: {e.path}"), action="OK"
                        )
                    )
                except Exception as ex:
                    page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text(f"保存失败: {str(ex)}"),
                            bgcolor=ft.Colors.RED,
                        )
                    )

        def compare_files(e):
            if not self.file1_path or not self.file2_path:
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("请先选择两个JSON文件"),
                        bgcolor=ft.Colors.ORANGE,
                    )
                )
                return

            progress_ref.current.visible = True
            page.update()

            try:
                only_in_file1, only_in_file2, common_keys = self.compare_json_files(
                    self.file1_path, self.file2_path
                )

                # 清空之前的结果
                result_ref.current.controls.clear()

                # 显示统计信息
                file1_name = Path(self.file1_path).name
                file2_name = Path(self.file2_path).name

                stats_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "比较结果统计", size=18, weight=ft.FontWeight.BOLD
                                ),
                                ft.Divider(),
                                ft.Text(
                                    f"{file1_name} 总key数: {len(only_in_file1) + len(common_keys)}"
                                ),
                                ft.Text(
                                    f"{file2_name} 总key数: {len(only_in_file2) + len(common_keys)}"
                                ),
                                ft.Text(
                                    f"共有key数: {len(common_keys)}",
                                    color=ft.Colors.GREEN,
                                ),
                                ft.Text(
                                    f"仅存在于 {file1_name} 的key数: {len(only_in_file1)}",
                                    color=ft.Colors.ORANGE
                                    if only_in_file1
                                    else ft.Colors.GREEN,
                                ),
                                ft.Text(
                                    f"仅存在于 {file2_name} 的key数: {len(only_in_file2)}",
                                    color=ft.Colors.ORANGE
                                    if only_in_file2
                                    else ft.Colors.GREEN,
                                ),
                            ]
                        ),
                        padding=15,
                    )
                )
                result_ref.current.controls.append(stats_card)

                # 显示缺失的key
                if only_in_file1:
                    missing_keys1 = ft.ExpansionTile(
                        title=ft.Text(
                            f"仅存在于 {file1_name} 的key ({len(only_in_file1)}个)"
                        ),
                        subtitle=ft.Text("点击展开查看详情", color=ft.Colors.GREY),
                        controls=[
                            ft.ListView(
                                [
                                    ft.ListTile(title=ft.Text(key))
                                    for key in sorted(only_in_file1)
                                ],
                                height=200,
                                spacing=1,
                            )
                        ],
                    )
                    result_ref.current.controls.append(missing_keys1)

                if only_in_file2:
                    missing_keys2 = ft.ExpansionTile(
                        title=ft.Text(
                            f"仅存在于 {file2_name} 的key ({len(only_in_file2)}个)"
                        ),
                        subtitle=ft.Text("点击展开查看详情", color=ft.Colors.GREY),
                        controls=[
                            ft.ListView(
                                [
                                    ft.ListTile(title=ft.Text(key))
                                    for key in sorted(only_in_file2)
                                ],
                                height=200,
                                spacing=1,
                            )
                        ],
                    )
                    result_ref.current.controls.append(missing_keys2)

                # 如果没有差异
                if not only_in_file1 and not only_in_file2:
                    result_ref.current.controls.append(
                        ft.Container(
                            content=ft.Text(
                                "✅ 两个文件的key完全匹配！",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREEN,
                            ),
                            alignment=ft.alignment.center,
                            padding=20,
                        )
                    )

            except Exception as ex:
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"比较失败: {str(ex)}"), bgcolor=ft.Colors.RED
                    )
                )
            finally:
                progress_ref.current.visible = False
                page.update()

        # 设置FilePicker的事件处理
        self.file_picker.on_result = on_file1_selected
        self.pick_files_dialog.on_result = on_file2_selected
        self.save_file_dialog.on_result = on_save_result

        # 将FilePicker添加到页面
        page.overlay.extend(
            [self.file_picker, self.pick_files_dialog, self.save_file_dialog]
        )

        # 创建UI组件
        header = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "JSON语言包比较工具",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE,
                    ),
                    ft.Text(
                        "上传两个JSON格式的语言包文件，比较它们的key差异",
                        size=14,
                        color=ft.Colors.GREY,
                    ),
                ]
            ),
            padding=ft.padding.only(bottom=20),
        )

        file_selection = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("文件选择", size=18, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "选择文件1",
                                    icon=ft.Icons.UPLOAD_FILE,
                                    on_click=lambda _: self.file_picker.pick_files(
                                        allow_multiple=False,
                                        allowed_extensions=["json"],
                                    ),
                                ),
                                ft.Text("未选择文件", ref=file1_ref, size=14),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "选择文件2",
                                    icon=ft.Icons.UPLOAD_FILE,
                                    on_click=lambda _: self.pick_files_dialog.pick_files(
                                        allow_multiple=False,
                                        allowed_extensions=["json"],
                                    ),
                                ),
                                ft.Text("未选择文件", ref=file2_ref, size=14),
                            ]
                        ),
                    ]
                ),
                padding=15,
            )
        )

        action_buttons = ft.Row(
            [
                ft.ElevatedButton(
                    "开始比较",
                    icon=ft.Icons.COMPARE,
                    on_click=compare_files,
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE),
                ),
                ft.ElevatedButton(
                    "保存报告",
                    icon=ft.Icons.SAVE,
                    on_click=lambda _: self.save_file_dialog.save_file(
                        allowed_extensions=["txt"],
                        file_name="json_comparison_report.txt",
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        progress_bar = ft.ProgressBar(ref=progress_ref, visible=False, width=400)

        results_section = ft.Column(ref=result_ref, scroll=ft.ScrollMode.ADAPTIVE)

        # 组装页面
        page.add(
            header,
            file_selection,
            action_buttons,
            ft.Container(progress_bar, alignment=ft.alignment.center),
            results_section
        )

def main(page: ft.Page):
    app = JSONComparatorApp()
    app.main(page)

if __name__ == "__main__":
    ft.app(target=main)