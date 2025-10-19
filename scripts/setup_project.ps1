\
        Param(
            [string]$Repo = "Braziliation"
        )
        New-Item -ItemType Directory -Path $Repo -Force | Out-Null
        Set-Location $Repo
        "Assets/Art","Assets/Audio","Assets/Sprites","Assets/UI","Assets/Tilemaps" | % { New-Item -ItemType Directory -Path $_ -Force | Out-Null }
        "Docs/Design","Docs/ArtStyle","Docs/Tech","Docs/Roadmap" | % { New-Item -ItemType Directory -Path $_ -Force | Out-Null }
        "Scripts/Player","Scripts/Enemies","Scripts/Managers","Scripts/UI" | % { New-Item -ItemType Directory -Path $_ -Force | Out-Null }
        New-Item -ItemType Directory -Path Tests/Unit -Force | Out-Null

        @"
        # Braziliation
        Jogo plataforma 2D em pixel art (C#) — ambientação dieselpunk pós-apocalíptica brasileira.
        "@ | Out-File README.md -Encoding UTF8

        @"
        MIT License
        Copyright (c) 2025 Braziliation
        "@ | Out-File LICENSE -Encoding UTF8

        Invoke-WebRequest -Uri "https://raw.githubusercontent.com/github/gitignore/main/Unity.gitignore" -OutFile .gitignore -UseBasicParsing -ErrorAction SilentlyContinue
        git init
        git lfs install 2>$null || $null
        git add .
        git commit -m "Initial project skeleton for Braziliation"
        Write-Host "Estrutura criada. Adicione o remote e faça push para o repositório remoto."
