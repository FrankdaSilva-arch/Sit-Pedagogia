def inscricao_curso(request, curso_id):
    print("View inscricao_curso foi chamada!")
    curso = get_object_or_404(Curso, id=curso_id)
    print("Curso encontrado:", curso)
    print("Atributos do curso:", curso.__dict__)
    # Tente acessar os possíveis campos
    try:
        print("curso.vagas_disponiveis:", curso.vagas_disponiveis)
    except AttributeError:
        print("curso.vagas_disponiveis não existe")
    try:
        print("curso.limite_vagas:", curso.limite_vagas)
    except AttributeError:
        print("curso.limite_vagas não existe")
    # Use o campo correto abaixo:
    vagas_disponiveis = getattr(curso, 'vagas_disponiveis', None) or getattr(curso, 'limite_vagas', None)
    print("Vagas disponíveis que serão enviadas ao template:", vagas_disponiveis)

    # Sua lógica de formulário
    form = InscricaoCursoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        # salvar inscrição, etc.
        pass

    return render(request, 'eventos/inscricao_curso.html', {
        'form': form,
        'vagas_disponiveis': vagas_disponiveis,
    }) 