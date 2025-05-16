from django.shortcuts import render, get_object_or_404, redirect, resolve_url

def input(request):
    '''들어오고 나오는 것을 처리.'''
    context = {}
    #  폼을 통해 들어온 데이터를 받는다.

    return render(request, 'utility/latex/render.html', context)

import os
import subprocess
from django.http import JsonResponse
from django.conf import settings
from django.utils.crypto import get_random_string
import json


def render_latex(request):
    if request.method == "POST":
        data = json.loads(request.body)
        latex_code = data.get("latex", "")

        filename = get_random_string(10)
        tex_filename = f"{filename}.tex"
        pdf_filename = f"{filename}.pdf"

        tex_path = os.path.join(settings.MEDIA_ROOT, tex_filename)

        if r'\documentclass' in latex_code:
            full_tex = latex_code  # 이미 전체 문서 구조 있음
        else:
            full_tex = r"""\documentclass{article}
        \usepackage{amsmath}
        \usepackage{geometry}
        \geometry{margin=1in}
        \begin{document}
        """ + latex_code + r"""
        \end{document}
        """

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(full_tex)

        try:
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_filename],
                cwd=settings.MEDIA_ROOT,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # 임시 파일 정리
            for ext in [".aux", ".log", ".tex"]:
                try:
                    os.remove(os.path.join(settings.MEDIA_ROOT, f"{filename}{ext}"))
                except FileNotFoundError:
                    pass

            return JsonResponse({"pdf_url": f"/media/{pdf_filename}"})

        except subprocess.CalledProcessError:
            return JsonResponse({"error": "PDF 생성 실패(서버)"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
