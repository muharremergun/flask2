function deleteNote(noteId) {
    fetch("/delete-note", {
      method: "POST",
      body: JSON.stringify({ noteId: noteId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }

  function toggleFavorite(noteId) {
    fetch("/toggle-favorite", {
      method: "POST",
      body: JSON.stringify({ noteId: noteId }),
    })
    .then(response => {
      if (response.ok) {
        // Favori not başarıyla güncellendi, belki bir mesaj gösterebilirsiniz
        console.log("Favori not başarıyla güncellendi.");
      } else {
        // İstek başarısız oldu, belki bir hata mesajı gösterebilirsiniz
        console.error("Favori not güncellenirken bir hata oluştu.");
      }
      // Her durumda, sayfayı yeniden yükle
      window.location.reload();
    })
    .catch(error => {
      // İstek sırasında bir hata oluştu
      console.error("İstek sırasında bir hata oluştu:", error);
      // Belki bir hata mesajı gösterebilir ve sayfayı yeniden yükleyebilirsiniz
      window.location.reload();
    });
  }
  