FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app

COPY cert.pfx /https/cert.pfx

ENV ASPNETCORE_URLS="http://localhost+:9012;https://localhost+:9013"
ENV ASPNETCORE_Kestrel__Certificates__Default__Password="Classa9@123"
ENV ASPNETCORE_Kestrel__Certificates__Default__Path="/https/cert.pfx"

EXPOSE 9012
EXPOSE 9013

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY . .
RUN dotnet publish -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "talyapi.dll"]