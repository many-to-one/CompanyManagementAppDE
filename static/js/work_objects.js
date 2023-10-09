function submitFormObjects() {
    var form = document.getElementById("objects");
    form.submit();
  }

  function submitFormStatus() {
    var form = document.getElementById("status");
    form.submit();
  }

  function edit(pk) {
      console.log('UPDATE')
      var pk = pk
      window.location.href = update_wo.replace('0', pk);
  }