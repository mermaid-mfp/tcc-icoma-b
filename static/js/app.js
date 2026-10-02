(() => {
  const FIELD = "data-field-";

  // Rosca de métodos de pagamento (as cores vêm do servidor em data-ring)
  document.querySelectorAll("[data-ring]").forEach((el) => {
    if (el.dataset.ring) el.style.background = "conic-gradient(" + el.dataset.ring + ")";
  });

  // Filtros que se enviam sozinhos quando o valor muda
  document.querySelectorAll("[data-autosubmit]").forEach((el) => {
    el.addEventListener("change", () => el.form.requestSubmit());
  });

  // Despesa não tem forma de pagamento
  function syncType(dialog) {
    const form = dialog.querySelector("form");
    const checked = form && form.querySelector('input[name="type_trans"]:checked');
    const field = form && form.querySelector("[data-payment-field]");
    if (!checked || !field) return;
    const isSale = checked.value === "sale";
    field.hidden = !isSale;
    field.querySelector("select").disabled = !isSale;
  }

  // Abre um diálogo. O botão que o abriu pode trazer:
  //   data-action        endereço para onde o formulário é enviado
  //   data-title         título do diálogo
  //   data-field-NOME    valor para preencher o campo NOME
  //   data-view-CHAVE    texto para mostrar no elemento [data-view="CHAVE"]
  function openDialog(button) {
    const dialog = document.getElementById(button.dataset.openDialog);
    if (!dialog) return;

    const form = dialog.querySelector("form");
    if (form) {
      form.reset();
      form.action = button.dataset.action || form.dataset.defaultAction || form.action;

      button.getAttributeNames()
        .filter((attr) => attr.startsWith(FIELD))
        .forEach((attr) => {
          const name = attr.slice(FIELD.length);
          const value = button.getAttribute(attr);
          form.querySelectorAll('[name="' + name + '"]').forEach((input) => {
            if (input.type === "radio") input.checked = input.value === value;
            else input.value = value;
          });
        });

      // valor que não existe na lista (ex.: venda antiga sem forma de pagamento) vira a primeira opção
      form.querySelectorAll("select").forEach((select) => {
        if (select.selectedIndex === -1) select.selectedIndex = 0;
      });
    }

    const title = dialog.querySelector("[data-dialog-title]");
    if (title) title.textContent = button.dataset.title || title.dataset.defaultTitle;

    dialog.querySelectorAll("[data-view]").forEach((el) => {
      el.textContent = button.getAttribute("data-view-" + el.dataset.view) || "—";
    });

    syncType(dialog);
    dialog.showModal();
  }

  document.querySelectorAll("[data-open-dialog]").forEach((button) => {
    button.addEventListener("click", () => openDialog(button));
  });

  document.querySelectorAll("[data-close-dialog]").forEach((button) => {
    button.addEventListener("click", () => button.closest("dialog").close());
  });

  document.querySelectorAll("dialog").forEach((dialog) => {
    // Clicar fora da caixa fecha, mas só se o clique também começou fora
    // (evita fechar ao soltar o mouse depois de selecionar um texto)
    let pressedOnBackdrop = false;
    dialog.addEventListener("mousedown", (event) => { pressedOnBackdrop = event.target === dialog; });
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog && pressedOnBackdrop) dialog.close();
    });

    dialog.addEventListener("change", (event) => {
      if (event.target.name === "type_trans") syncType(dialog);
    });
  });
})();
