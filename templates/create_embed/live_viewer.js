    const inputs = {
      authorName: document.getElementById('authorName'),
      authorUrl: document.getElementById('authorUrl'),
      authorIconUrl: document.getElementById('authorIconUrl'),
      title: document.getElementById('title'),
      titleUrl: document.getElementById('titleUrl'),
      description: document.getElementById('description'),
      imageUrl: document.getElementById('imageUrl'),
      thumbnailUrl: document.getElementById('thumbnailUrl'),
      color: document.getElementById('color'),
      colorHex: document.getElementById('colorHex'),
      footerText: document.getElementById('footerText'),
      footerIconUrl: document.getElementById('footerIconUrl')
    };

    const preview = {
      embed: document.getElementById('embedPreview'),
      author: document.getElementById('pAuthor'),
      authorNameContainer: document.getElementById('pAuthorNameContainer'),
      authorIcon: document.getElementById('pAuthorIcon'),
      titleContainer: document.getElementById('pTitleContainer'),
      description: document.getElementById('pDescription'),
      image: document.getElementById('pImage'),
      thumbnail: document.getElementById('pThumbnail'),
      footer: document.getElementById('pFooter'),
      footerText: document.getElementById('pFooterText'),
      footerIcon: document.getElementById('pFooterIcon')
    };

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

    function updatePreview() {
      preview.embed.style.borderColor = inputs.color.value;

      if (inputs.authorName.value.trim()) {
        const nameText = inputs.authorName.value;
        const authorUrl = inputs.authorUrl.value.trim();

        if (authorUrl) {
          preview.authorNameContainer.innerHTML = `<a href="${authorUrl}" target="_blank" class="embed-author-name">${nameText}</a>`;
        } else {
          preview.authorNameContainer.innerHTML = `<span class="embed-author-name">${nameText}</span>`;
        }

        preview.author.style.display = 'flex';
        
        if (inputs.authorIconUrl.value.trim()) {
          preview.authorIcon.src = inputs.authorIconUrl.value;
          preview.authorIcon.style.display = 'block';
        } else {
          preview.authorIcon.style.display = 'none';
        }
      } else {
        preview.author.style.display = 'none';
      }

      if (inputs.title.value.trim()) {
        const titleText = inputs.title.value;
        const titleUrl = inputs.titleUrl.value.trim();

        if (titleUrl) {
          preview.titleContainer.innerHTML = `<a href="${titleUrl}" target="_blank" class="embed-title">${titleText}</a>`;
        } else {
          preview.titleContainer.innerHTML = `<div class="embed-title">${titleText}</div>`;
        }
      } else {
        preview.titleContainer.innerHTML = '';
      }

      if (inputs.description.value.trim()) {
        preview.description.innerHTML = parseDiscordMarkdown(inputs.description.value);
        preview.description.style.display = 'block';
      } else {
        preview.description.style.display = 'none';
      }

      if (inputs.imageUrl.value.trim()) {
        preview.image.src = inputs.imageUrl.value;
        preview.image.style.display = 'block';
      } else {
        preview.image.style.display = 'none';
      }

      if (inputs.thumbnailUrl.value.trim()) {
        preview.thumbnail.src = inputs.thumbnailUrl.value;
        preview.thumbnail.style.display = 'block';
      } else {
        preview.thumbnail.style.display = 'none';
      }

      if (inputs.footerText.value.trim()) {
        preview.footerText.textContent = inputs.footerText.value;
        preview.footer.style.display = 'flex';
        if (inputs.footerIconUrl.value.trim()) {
          preview.footerIcon.src = inputs.footerIconUrl.value;
          preview.footerIcon.style.display = 'block';
        } else {
          preview.footerIcon.style.display = 'none';
        }
      } else {
        preview.footer.style.display = 'none';
      }
    }

    Object.values(inputs).forEach(input => {
      input.addEventListener('input', updatePreview);
    });

    inputs.color.addEventListener('input', (e) => {
      inputs.colorHex.value = e.target.value;
    });
    inputs.colorHex.addEventListener('input', (e) => {
      if (/^#[0-9A-F]{6}$/i.test(e.target.value)) {
        inputs.color.value = e.target.value;
        updatePreview();
      }
    });