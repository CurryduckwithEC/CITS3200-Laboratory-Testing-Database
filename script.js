async function renderData() {
    const csvUrl = '../cleaned.csv';  

    Papa.parse(csvUrl, {
        download: true,
        header: true,
        complete: function(results) {
            const data = results.data;

            // got the data columns
            const time = data.map(row => parseFloat(row['Time start of stage ']));
            const axialStrain = data.map(row => parseFloat(row['Axial strain']));
            const volStrain = data.map(row => parseFloat(row['Vol strain']));
            const pPrime = data.map(row => parseFloat(row["p'"]));
            const q = data.map(row => parseFloat(row['q']));
            const shearPWP = data.map(row => parseFloat(row['Shear induced PWP']));
            const sigma1 = data.map(row => parseFloat(row["σ'1"])); 
            const sigma3 = data.map(row => parseFloat(row["σ'3"])); 
       
            // 1. Stress (kPa) vs. Time (hours)
            Plotly.newPlot('stress_vs_time', [
                { x: axialStrain, y: pPrime, mode: 'lines', name: "p'" },
                { x: axialStrain, y: q, mode: 'lines', name: 'q' },
                { x: axialStrain, y: shearPWP, mode: 'lines', name: 'PWP' }
            ]);

            // 2. Axial and Volumetric Strain (%) vs. Time (hours)
            Plotly.newPlot('strain_vs_time', [
                { x: time, y: axialStrain, mode: 'lines', name: 'Axial Strain (%)' },
                { x: time, y: volStrain, mode: 'lines', name: 'Volumetric Strain (%)' }
            ]);

            // 3. Deviator and Mean Effective Stress (q and p') vs. Axial Strain, ea (%)
            Plotly.newPlot('stress_vs_axial_strain', [
                { x: axialStrain, y: pPrime, mode: 'lines', name: 'Mean Effective Stress (p\')' },
                { x: axialStrain, y: q, mode: 'lines', name: 'Deviator Stress (q)' }
            ]);

            // 4. Shear-induced Pore Pressure (kPa) vs. Axial Strain, ea (%)
            Plotly.newPlot('pore_pressure_vs_axial_strain', [{
                x: axialStrain,
                y: shearPWP,
                mode: 'lines',
                name: 'Shear-induced Pore Pressure (kPa)'
            }]);

            // 5. Stress Ratio (q/p') vs. Axial Strain, ea (%)
            const stressRatio = q.map((value, index) => value / pPrime[index]);
            Plotly.newPlot('stress_ratio_vs_axial_strain', [{
                x: axialStrain,
                y: stressRatio,
                mode: 'lines',
                name: 'Stress Ratio (q/p\')'
            }]);

            // 6. Deviator Stress (q) vs. Mean Effective Stress (p')
            Plotly.newPlot('axial_strain_vs_mean_effective_stress', [{
                x: pPrime,
                y: q,
                mode: 'lines',
                name: 'Deviator Stress (q)'
            }]);
        }
    });
}

renderData();
