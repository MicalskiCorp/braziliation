\
        Param (
            [Parameter(Mandatory=$true)]
            [string]$NewVersion
        )

        # Update VERSION file
        Set-Content -Path "./VERSION" -Value $NewVersion
        Write-Host "✅ Versão atualizada para $NewVersion"

        # Commit, tag and push (assumes git remote 'origin' is configured and user has permissions)
        git add VERSION
        git commit -m "chore: atualiza versão para $NewVersion"
        git tag "v$NewVersion"
        git push origin --tags

        Write-Host "✅ Commit e tag enviados para o remoto (v$NewVersion)"
