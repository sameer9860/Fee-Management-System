<input type="file" id="csvInput" accept=".csv" />

<script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.2/papaparse.min.js"></script>
<script>
document.getElementById("csvInput").addEventListener("change", function(e) {
    const file = e.target.files[0];

    Papa.parse(file, {
        header: true, // treat first row as headers
        skipEmptyLines: true,
        complete: function(results) {
            // results.data is an array of rows
            console.log("Parsed Data:", results.data);

            // Send in chunks via AJAX
            fetch("/api/upload-students/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ students: results.data })
            })
            .then(res => res.json())
            .then(data => console.log("Upload success:", data));
        }
    });
});
</script>
