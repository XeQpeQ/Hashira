local UserInputService = game:GetService("UserInputService")
local Players = game:GetService("Players")

local gui, mainFrame, originalSize, isExpanded

local bb = game:GetService('VirtualUser')

game:GetService('Players').LocalPlayer.Idled:Connect(function()
    bb:CaptureController()
    bb:ClickButton2(Vector2.new())
    --[[
    Se necesita una referencia al objeto 'ab' para actualizar su texto. 
    Asumiré que 'ab' es un objeto GUI TextLabel definido en algún lugar del código que no fue proporcionado.
    Si 'ab' no está definido, necesitarás cambiarlo por una referencia válida al objeto TextLabel.
    ]]
    -- ab.Text = "Roblox intentó expulsarte, pero lo evité"
    -- wait(2)
    -- ab.Text = "Estado: Activo"
end)

local HashiraUI = loadstring(game:HttpGet("https://raw.githubusercontent.com/XeQpeQ/Hashira/main/UI2.lua"))()
local win = HashiraUI:Create({
    Name = "Hashira Hub",
    StartupSound = {
        Toggle = false,
        SoundID = "rbxassetid://6958727243",
        TimePosition = 1
    }
})

local LP = game.Players.LocalPlayer
local FarmMethod = "Above"
local tweenspeed = 30
local Distance = 10

local function GetDistance(Endpoint)
    if typeof(Endpoint) == "Instance" or typeof(Endpoint) == "CFrame" then
        Endpoint = Vector3.new(Endpoint.Position.X, game.Players.LocalPlayer.Character.HumanoidRootPart.Position.Y, Endpoint.Position.Z)
    end
    local Magnitude = (Endpoint - game.Players.LocalPlayer.Character.HumanoidRootPart.Position).Magnitude
    return Magnitude
end

local function Tween(Endpoint)
    if typeof(Endpoint) == "Instance" then
        Endpoint = Endpoint.CFrame
    end
    local TweenFunc = {}
    local Distance = GetDistance(Endpoint)
    local TweenInfo = game:GetService("TweenService"):Create(game.Players.LocalPlayer.Character.HumanoidRootPart, TweenInfo.new(Distance / tweenspeed, Enum.EasingStyle.Linear), {CFrame = Endpoint * CFrame.fromAxisAngle(Vector3.new(1, 0, 0), math.rad(0))})
    TweenInfo:Play()
    function TweenFunc:Cancel()
        TweenInfo:Cancel()
        return false
    end
    if Distance <= 5 then
        game.Players.LocalPlayer.Character.HumanoidRootPart.CFrame = Endpoint
        TweenInfo:Cancel()
        return false
    end
    return TweenFunc
end

task.spawn(function()
    while wait() do
        pcall(function()
            -- Define farming methods based on FarmMethod value
            if FarmMethod == "Above" then
                FarmModes = CFrame.new(0,Distance,0) * CFrame.Angles(math.rad(-90),0,0) 
            elseif FarmMethod == "Below" then
                FarmModes = CFrame.new(0,-Distance,0) * CFrame.Angles(math.rad(90),0,0)
            elseif FarmMethod == "Behind" then
                FarmModes = CFrame.new(0,0,Distance)
            elseif FarmMethod == "Ahead" then
                FarmModes = CFrame.new(0, 0, -Distance)
                local rotation = CFrame.Angles(0, math.rad(180), 0)
                FarmModes = FarmModes * rotation
            end
        end)
    end
end)

local AutoFarm = win:Tab('AutoFarm')
local uitab = win:Tab('UI')

uitab:Button('Destroy GUI', function()
    win:Exit()
end)

AutoFarm:Toggle('Auto Zangetsu', function(v)
    getgenv().AutoBandit = v
end)

AutoFarm:Toggle('Auto Sword', function(v)
    getgenv().AutoSword = v
end)

AutoFarm:Button('No Stamina', function()
    local Namecall
    Namecall = hookmetamethod(game, '__namecall', function(self, ...)
        local Args = {...}
        local method = getnamecallmethod()

        if method == 'FireServer' and self.Name == 'takestam' then 
            return nil
        end 

        return Namecall(self, ...)
    end)
end)

spawn(function()
    while wait(.5) do
        if getgenv().AutoBandit then
local args = {
    [1] = "Gochutekkan",
    [2] = workspace.World.Live.Mobs.Zanpakuto.Zangetsu.HumanoidRootPart.Position
}

game:GetService("ReplicatedStorage"):WaitForChild("Remotes"):WaitForChild("Server"):WaitForChild("Initiate_Server"):FireServer(unpack(args))
            
            local Player = game:GetService("Players").LocalPlayer
            pcall(function()
                if Player.Backpack:FindFirstChild("Zanpakuto") and Player.Character:FindFirstChild("Zanpakuto") == nil then
                    local tool = Player.Backpack:FindFirstChild("Zanpakuto")
                    Player.Character.Humanoid:EquipTool(tool)
                end
            end)
        end
    end
end)
spawn(function()
    while wait() do
        if getgenv().AutoSword then
        if game.Players.LocalPlayer.PlayerGui.HUD.Holder.Bars.SwordBar.Visible == false then
                for i, v in pairs(game:GetService("Workspace").World.Map["Sword Locations"]:GetChildren()) do
    local swordNumber = tonumber(string.match(v.Name, "pickedSword(%d+)"))
    if swordNumber and swordNumber >= 1 and swordNumber <= 50 then
        local proximityPrompt = v:FindFirstChildWhichIsA("ProximityPrompt", true)
        if proximityPrompt then
            fireproximityprompt(proximityPrompt, 0, true)
        end
    end
end
            end
    end
end
end)

