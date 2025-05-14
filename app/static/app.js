window.addEventListener('DOMContentLoaded', () => {
    // Only run chat app JS if #chat exists (i.e., not on login/setup pages)
    if (!document.getElementById('chat')) return;
    const userId = window.USER_ID;
    const personas = window.PERSONAS || [];
    const personaSelect = document.getElementById('persona-select');
    const win = document.getElementById('window');
    const msgInput = document.getElementById('msg');
    let currentConversationId = null;
    let pendingDeleteId = null;
    let deleteModal = null;
  
    // Sidebar for conversations
    let sidebar = document.getElementById('sidebar');
    if (!sidebar) {
      sidebar = document.createElement('div');
      sidebar.id = 'sidebar';
      sidebar.style.width = '260px';
      sidebar.style.position = 'absolute';
      sidebar.style.left = '0';
      sidebar.style.top = '0';
      sidebar.style.bottom = '0';
      sidebar.style.background = '#f3f7fa';
      sidebar.style.borderRight = '1.5px solid #b3e5fc';
      sidebar.style.overflowY = 'auto';
      sidebar.style.padding = '1.5rem 0.5rem 1.5rem 1.5rem';
      sidebar.style.zIndex = '10';
      document.body.appendChild(sidebar);
      document.getElementById('chat').style.marginLeft = '260px';
    }

    async function apiFetch(path, opts = {}) {
      opts.credentials = 'include';
      opts.headers = Object.assign(
        { 'X-Requested-With': 'XMLHttpRequest' },
        opts.headers || {}
      );
      return fetch(path, opts);
    }
  
    async function loadConversations() {
      // Show loading message
      sidebar.innerHTML = '<h4>Conversations</h4><div class="text-muted">Loading conversations...</div>';
      const resp = await apiFetch('/conversations');
      const contentType = resp.headers.get('content-type');
      if (!resp.ok || !contentType || !contentType.includes('application/json')) {
        alert('Session expired or server error. Please log in again.');
        await apiFetch('/auth/logout', { method: 'POST' });
        window.location.href = '/login';
        return;
      }
      let data;
      try {
        data = await resp.json();
      } catch (e) {
        alert('Session expired or server error. Please log in again.');
        await apiFetch('/auth/logout', { method: 'POST' });
        window.location.href = '/login';
        return;
      }
      // Defensive: sort conversations by started_at descending (most recent first)
      if (data.conversations) {
        data.conversations.sort((a, b) => new Date(b.started_at) - new Date(a.started_at));
      }
      // Replace loading message with conversation list
      sidebar.innerHTML = '<h4>Conversations</h4>';
      const list = document.createElement('ul');
      list.className = 'list-group';
      (data.conversations || []).forEach(conv => {
        const li = document.createElement('li');
        li.className = 'list-group-item conversation-summary d-flex justify-content-between align-items-center';
        const snippetSpan = document.createElement('span');
        snippetSpan.textContent = conv.snippet || '(No message)';
        snippetSpan.style.cursor = 'pointer';
        snippetSpan.onclick = () => loadConversation(conv.id);
        li.appendChild(snippetSpan);
        // Delete button
        const delBtn = document.createElement('button');
        delBtn.className = 'btn btn-danger btn-sm ms-2';
        delBtn.textContent = '×';
        delBtn.title = 'Delete conversation';
        delBtn.onclick = (e) => {
          console.log('Delete button clicked for conversation', conv.id);
          e.stopPropagation();
          pendingDeleteId = conv.id;
          if (!deleteModal) {
            // fallback: try to initialize if not already
            const modalElem = document.getElementById('deleteConfirmModal');
            if (modalElem && window.bootstrap) {
              deleteModal = new window.bootstrap.Modal(modalElem);
            }
          }
          if (deleteModal) deleteModal.show();
        };
        li.appendChild(delBtn);
        if (conv.id === currentConversationId) li.classList.add('active');
        list.appendChild(li);
      });
      sidebar.appendChild(list);
      const newBtn = document.createElement('button');
      newBtn.className = 'btn btn-primary btn-sm mt-3';
      newBtn.textContent = 'New Conversation';
      newBtn.onclick = startNewConversation;
      sidebar.appendChild(newBtn);
    }
  
    async function loadConversation(conversationId) {
      currentConversationId = conversationId;
      win.innerHTML = '';
      const resp = await apiFetch(`/conversations/${conversationId}`);
      const contentType = resp.headers.get('content-type');
      if (!resp.ok || !contentType || !contentType.includes('application/json')) {
        alert('Session expired or server error. Please log in again.');
        await apiFetch('/auth/logout', { method: 'POST' });
        window.location.href = '/login';
        return;
      }
      let data;
      try {
        data = await resp.json();
      } catch (e) {
        alert('Session expired or server error. Please log in again.');
        window.location.href = '/login';
        return;
      }
      (data.messages || []).forEach(m => {
        const div = document.createElement('div');
        div.className = 'message ' + (m.sender === 'user' ? 'user' : 'bot');
        div.textContent = m.content;
        win.appendChild(div);
      });
      highlightActiveConversation();
      win.scrollTop = win.scrollHeight;
    }
  
    function highlightActiveConversation() {
      document.querySelectorAll('.conversation-summary').forEach(li => {
        li.classList.remove('active');
        if (li.onclick && li.onclick.toString().includes(currentConversationId)) {
          li.classList.add('active');
        }
      });
    }
  
    async function startNewConversation() {
      const resp = await apiFetch('/conversations', { method: 'POST' });
      const contentType = resp.headers.get('content-type');
      if (!resp.ok || !contentType || !contentType.includes('application/json')) {
        alert('Session expired or server error. Please log in again.');
        window.location.href = '/login';
        return;
      }
      let data;
      try {
        data = await resp.json();
      } catch (e) {
        alert('Session expired or server error. Please log in again.');
        window.location.href = '/login';
        return;
      }
      currentConversationId = data.id;
      win.innerHTML = '';
      await loadConversations();
    }
  
    // Configure marked for safe rendering
    marked.setOptions({
      breaks: true,  // Convert \n to <br>
      sanitize: true // Prevent XSS
    });
  
    // Populate persona selector
    for (const persona of personas) {
      const opt = document.createElement('option');
      opt.value = persona.id;
      opt.textContent = persona.name;
      personaSelect.appendChild(opt);
    }
    
  
    document.getElementById('send').addEventListener('click', async function sendClick(e) {
      e.preventDefault();
      const message = msgInput.value.trim();
      if (!message) return;
      const persona_id = personaSelect.value;
      if (!persona_id) {
        alert('Please select a persona.');
        return;
      }

      // Save current state for rollback
      const prevWinHTML = win.innerHTML;
      const prevSidebarHTML = sidebar.innerHTML;

      // Optimistically update UI
      const u = document.createElement('div');
      u.className = 'message user';
      u.textContent = message;
      win.appendChild(u);

      // Show pending bot response
      const pendingBot = document.createElement('div');
      pendingBot.className = 'message bot';
      pendingBot.textContent = '...';
      win.appendChild(pendingBot);

      msgInput.value = '';
      win.scrollTop = win.scrollHeight;

      try {
        // Start new conversation if needed
        if (!currentConversationId) {
          await startNewConversation();
        }

        // Fetch bot response and save both messages
        const resp = await apiFetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message, persona_id, conversation_id: currentConversationId })
        });
        const contentType = resp.headers.get('content-type');
        if (!resp.ok || !contentType || !contentType.includes('application/json')) {
          throw new Error('Session expired or server error.');
        }
        let j;
        try {
          j = await resp.json();
        } catch (e) {
          throw new Error('Session expired or server error.');
        }
        if (j.conversation_id) currentConversationId = j.conversation_id;

        // Update UI with real bot response
        pendingBot.innerHTML = marked.parse(j.response || j.error);

        // Update only the current conversation's summary in the sidebar
        try {
          // Fetch the latest summary for this conversation
          const convResp = await apiFetch(`/conversations`);
          if (convResp.ok) {
            const convData = await convResp.json();
            const updatedConv = (convData.conversations || []).find(c => c.id === currentConversationId);
            if (updatedConv) {
              // Find the sidebar list item for this conversation
              const sidebarItems = sidebar.querySelectorAll('.conversation-summary');
              sidebarItems.forEach(li => {
                const snippetSpan = li.querySelector('span');
                if (snippetSpan && li.classList.contains('active')) {
                  snippetSpan.textContent = updatedConv.snippet || '(No message)';
                }
              });
            }
          }
        } catch (e) {
          // Ignore sidebar update errors
        }

        // Update chat window with backend state
      } catch (err) {
        // Rollback UI
        win.innerHTML = prevWinHTML;
        sidebar.innerHTML = prevSidebarHTML;
        alert(err.message || 'Failed to send message. Please try again.');
      }
    });
  
    document.getElementById('confirmDeleteBtn').onclick = async () => {
      if (pendingDeleteId !== null) {
        const delResp = await apiFetch(`/conversations/${pendingDeleteId}`, { method: 'DELETE' });
        if (delResp.ok) {
          if (currentConversationId === pendingDeleteId) {
            currentConversationId = null;
            win.innerHTML = '';
          }
          await loadConversations();
        } else {
          alert('Failed to delete conversation.');
        }
        pendingDeleteId = null;
        if (deleteModal) deleteModal.hide();
      }
    };
  
    // Ensure modal is initialized after DOMContentLoaded
    document.addEventListener('DOMContentLoaded', () => {
      const modalElem = document.getElementById('deleteConfirmModal');
      if (modalElem && window.bootstrap) {
        deleteModal = new window.bootstrap.Modal(modalElem);
      }
    });
    
    // Initial load
    loadConversations();
    // Start a new conversation if none is loaded
    if (!currentConversationId) {
      startNewConversation();
    }
  });