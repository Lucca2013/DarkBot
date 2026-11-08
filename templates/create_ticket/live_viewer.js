document.addEventListener('DOMContentLoaded', () => {
  const inputs = {
    title: document.getElementById('title'),
    description: document.getElementById('description'),
    footerText: document.getElementById('footerText'),
    color: document.getElementById('color'),
    colorHex: document.getElementById('colorHex'),
    rolesToMark: document.getElementById('roles_to_mark'),
    ticketMessage: document.getElementById('ticket_message')
  };

  const previewPanel = {
    embed: document.getElementById('embedPreview'),
    title: document.getElementById('pTitle'),
    description: document.getElementById('pDescription'),
    footer: document.getElementById('pFooter'),
    footerText: document.getElementById('pFooterText')
  };

  const previewCreatedTicket = {
    embed: document.getElementById('ticketEmbedPreview'),
    message: document.getElementById('pTicketMessage'),
    roles: document.getElementById('pRolesMentioned')
  };

  const selectMenuPreview = document.getElementById('pSelectMenu');

  function parseDiscordMarkdown(text) {
    if (!text) return '';

    let escaped = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    return escaped
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')       // **bold**
      .replace(/__(.*?)__/g, '<u>$1</u>')                    // __underline__
      .replace(/\*(.*?)\*/g, '<em>$1</em>')                  // *italic*
      .replace(/_(.*?)_/g, '<em>$1</em>')                    // _italic_
      .replace(/~~(.*?)~~/g, '<del>$1</del>')                // ~~strikethrough~~
      .replace(/`(.*?)`/g, '<code>$1</code>');               // `code`
  }

  function getSelectedRolesText() {
    if (!inputs.rolesToMark) return '';
    const selected = Array.from(inputs.rolesToMark.selectedOptions).map(opt => `@${opt.text.replace(/^@/, '')}`);
    return selected.join(' ');
  }

  function updateSelectMenuPreview() {
    if (!selectMenuPreview) return;

    const optionItems = document.querySelectorAll('#options-container .option-item');
    
    if (optionItems.length === 0) {
      selectMenuPreview.innerHTML = '<div style="color: #949ba4; font-size: 14px;">Select an option...</div>';
      return;
    }

    let html = '<div style="color: #b5bac1; font-size: 13px; margin-bottom: 8px; font-weight: 600;">Select an option...</div>';
    
    optionItems.forEach(item => {
      const emoji = item.querySelector('.opt-emoji')?.value.trim() || '';
      const label = item.querySelector('.opt-label')?.value.trim() || '';
      const desc = item.querySelector('.opt-description')?.value.trim() || '';

      html += `
        <div style="display: flex; align-items: flex-start; gap: 10px; padding: 6px 8px; background: #2b2d31; border-radius: 4px; margin-bottom: 4px;">
          <span style="font-size: 18px; line-height: 1.2;">${emoji}</span>
          <div style="display: flex; flex-direction: column;">
            <strong style="color: #f2f3f5; font-size: 14px; font-weight: 500;">${parseDiscordMarkdown(label)}</strong>
            ${desc ? `<span style="color: #949ba4; font-size: 12px;">${parseDiscordMarkdown(desc)}</span>` : ''}
          </div>
        </div>
      `;
    });

    selectMenuPreview.innerHTML = html;
  }

  function updatePreview() {
    const currentColor = inputs.color ? inputs.color.value : '#5865f2';

    if (previewPanel.embed) {
      previewPanel.embed.style.borderColor = currentColor;
    }

    if (previewPanel.title) {
      const titleVal = inputs.title.value ? inputs.title.value.trim() : '';
      if (titleVal) {
        previewPanel.title.textContent = titleVal;
        previewPanel.title.style.display = 'block';
      } else {
        previewPanel.title.style.display = 'none';
      }
    }

    if (previewPanel.description) {
      const descVal = inputs.description ? inputs.description.value.trim() : '';
      previewPanel.description.innerHTML = descVal ? parseDiscordMarkdown(descVal) : '';
    }

    if (previewPanel.footer && previewPanel.footerText) {
      const footerVal = inputs.footerText.value ? inputs.footerText.value.trim() : '';
      if (footerVal) {
        previewPanel.footerText.textContent = footerVal;
        previewPanel.footer.style.display = 'flex';
      } else {
        previewPanel.footer.style.display = 'none';
      }
    }

    if (previewCreatedTicket.embed) {
      previewCreatedTicket.embed.style.borderColor = currentColor;
    }
    if (previewCreatedTicket.message) {
      const msgVal = inputs.ticketMessage ? inputs.ticketMessage.value.trim() : '';
      previewCreatedTicket.message.innerHTML = msgVal ? parseDiscordMarkdown(msgVal) : '';
    }
    if (previewCreatedTicket.roles) {
      const rolesText = getSelectedRolesText();
      previewCreatedTicket.roles.textContent = rolesText;
      previewCreatedTicket.roles.style.display = rolesText ? 'block' : 'none';
    }

    updateSelectMenuPreview();
  }

  Object.values(inputs).forEach(input => {
    if (input) {
      input.addEventListener('input', updatePreview);
      input.addEventListener('change', updatePreview);
    }
  });

  const optionsContainer = document.getElementById('options-container');
  if (optionsContainer) {
    optionsContainer.addEventListener('input', updatePreview);
    
    const observer = new MutationObserver(updatePreview);
    observer.observe(optionsContainer, { childList: true, subtree: true });
  }

  if (inputs.color && inputs.colorHex) {
    inputs.color.addEventListener('input', (e) => {
      inputs.colorHex.value = e.target.value;
      updatePreview();
    });

    inputs.colorHex.addEventListener('input', (e) => {
      if (/^#[0-9A-F]{6}$/i.test(e.target.value)) {
        inputs.color.value = e.target.value;
        updatePreview();
      }
    });
  }

  updatePreview();
});